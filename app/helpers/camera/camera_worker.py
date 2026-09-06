"""
camera_worker.py — Worker de captura de webcam → ASCII.

Implementa los hooks de BaseCaptureWorker para una fuente cv2.VideoCapture:

    _setup()        Apertura DSHOW → MSMF (fallback) con timeout por intento y
                    retries; negociación de formato MJPG + resolución en el orden
                    correcto para DSHOW (BUFFERSIZE → FOURCC → WIDTH → HEIGHT).
    _read_frame()   cap.read().
    _apply_params() Cambio de resolución en caliente cuando el usuario la modifica.
    _teardown()     cap.release().

Toda la lógica de threading, throttle de FPS, detección de lag, reconexión
automática y el pipeline ASCII vive ahora en BaseCaptureWorker. Este módulo
conserva el comportamiento de apertura tal cual estaba (timeouts, fallback de
backend, handle fantasma 0×0) para no cambiar en nada el modo cámara.
"""
import threading
import time
import cv2

from app.models.ascii_params_model import AsciiParams
from app.helpers.capture.base_capture_worker import BaseCaptureWorker
from typing import Callable

# ── Constantes de apertura ────────────────────────────────────────────────────
_OPEN_TIMEOUT     = 2.5  # Segundos máximos para que cv2.VideoCapture() abra el device.
                          # DSHOW/MSMF pueden bloquearse indefinidamente con drivers
                          # colgados; la apertura corre en hilo con join(timeout).
_MAX_OPEN_RETRIES = 3    # Intentos de apertura antes de declarar el índice inaccesible.


class CameraWorker(BaseCaptureWorker):
    """
    Worker de webcam. Hereda de BaseCaptureWorker todo el ciclo de vida.

    Constantes de reconexión / lag (heredadas y ajustadas para la C920):
        MAX_CONSECUTIVE_FAILURES = 10  → filtra drops momentáneos de USB.
        RECONNECT_DELAY          = 1.5 → da tiempo al driver a liberar el device.
        MAX_RECONNECT_TOTAL      = 3   → evita el bucle infinito con la cámara
                                        físicamente desconectada.
    """

    SOURCE_TAG               = "CAM"
    MAX_CONSECUTIVE_FAILURES = 10
    RECONNECT_DELAY          = 1.5
    MAX_RECONNECT_TOTAL      = 3

    def __init__(
        self,
        cam_index: int,
        params: AsciiParams,
        on_frame: Callable,
        on_status: Callable[[str, str], None] | None = None,
    ):
        """
        Args:
            cam_index : índice cv2 de la cámara a abrir (0, 1, 2…).
            params    : AsciiParams compartido con el hilo principal (leído bajo lock).
            on_frame  : callback(AsciiFrame | None). None indica error fatal.
            on_status : callback(msg, level) para la UI.
        """
        super().__init__(params, on_frame, on_status)
        self._cam_index   = cam_index
        self._cap: cv2.VideoCapture | None = None
        self._current_res: tuple | None = None

    # ── Mensajes específicos de cámara ────────────────────────────────────

    def _msg_reconnecting(self, count: int, total: int) -> str:
        return f"Stream cortado — reconectando ({count}/{total})…"

    def _msg_reconnect_failed(self) -> str:
        return "Reconexión fallida — desconecta y vuelve a conectar el cable USB"

    def _msg_fatal_disconnect(self) -> str:
        return "Cámara desconectada — desconecta y vuelve a conectar el cable USB"

    def _msg_lag(self, avg_ms: float) -> str:
        return (
            f"Cámara lenta ({avg_ms:.0f} ms/frame) — "
            "reduce Columnas, FPS o Resolución para evitar desconexión"
        )

    # ── Apertura ─────────────────────────────────────────────────────────────

    def _open_cap(self, index: int) -> cv2.VideoCapture | None:
        """
        Prueba DSHOW primero y MSMF como fallback.
        Orden correcto de propiedades para negociar resolución alta:
          BUFFERSIZE → FOURCC → WIDTH → HEIGHT
        """
        w_req, h_req = self._params.resolution

        for backend, name in [(cv2.CAP_DSHOW, "DSHOW"), (cv2.CAP_MSMF, "MSMF")]:
            if self._stop_event.is_set():
                return None

            cap_holder: list[cv2.VideoCapture | None] = [None]

            def _open(b=backend):
                try:
                    c = cv2.VideoCapture(index, b)
                    if c.isOpened():
                        cap_holder[0] = c
                    else:
                        c.release()
                except Exception:
                    pass

            t = threading.Thread(target=_open, daemon=True)
            t.start()
            t.join(timeout=_OPEN_TIMEOUT)

            cap = cap_holder[0]
            if cap is None or not cap.isOpened():
                continue

            # Verificar que no es un handle fantasma (cámara desconectada físicamente)
            actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_w == 0 and actual_h == 0:
                cap.release()
                continue  # handle abierto pero cámara no responde

            # Negociar formato y resolución en el orden correcto
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w_req)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h_req)
            except Exception:
                pass

            # Vaciar buffer inicial
            for _ in range(5):
                try:
                    cap.read()
                except Exception:
                    break

            self._status(f"Abierto con {name}")
            return cap

        return None

    def _open_with_retries(self, index: int) -> cv2.VideoCapture | None:
        for attempt in range(_MAX_OPEN_RETRIES):
            if self._stop_event.is_set():
                return None
            cap = self._open_cap(index)
            if cap is not None:
                return cap
            if attempt < _MAX_OPEN_RETRIES - 1:
                time.sleep(0.5)
        return None

    # ── Hooks de BaseCaptureWorker ───────────────────────────────────────

    def _setup(self) -> bool:
        cap = self._open_with_retries(self._cam_index)
        if cap is None:
            self._status(
                f"Índice {self._cam_index} no accesible — "
                "verifica que la cámara no esté en uso por otra app",
                "error",
            )
            return False

        self._cap         = cap
        self._current_res = self._params.resolution
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._status(f"Índice {self._cam_index} activo ({w}×{h})")
        return True

    def _apply_params(self, params: AsciiParams) -> None:
        new_res = params.resolution
        if new_res != self._current_res and self._cap is not None:
            try:
                rw, rh = new_res
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  rw)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, rh)
                self._current_res = new_res
            except Exception:
                pass

    def _read_frame(self) -> tuple[bool, "any"]:
        try:
            ret, frame_bgr = self._cap.read()
        except Exception as e:
            self._status(f"Excepción en cap.read(): {e}", "warn")
            return False, None
        return bool(ret), frame_bgr

    def _teardown(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
