"""
camera_worker.py — Thread de captura, procesado y entrega de frames ASCII.

Ciclo de vida:
    1. Apertura de la cámara (DSHOW → MSMF como fallback) con timeout por intento.
    2. Negociación de formato: FOURCC MJPG → resolución (orden necesario para DSHOW).
    3. Loop principal: captura → detección de lag → preprocesado → conversión ASCII
       → renderizado PNG → entrega via on_frame().
    4. Si el stream se corta, intenta reconexión automática hasta _MAX_RECONNECT_TOTAL.
    5. Si la cámara se desconecta físicamente (handle 0×0), avisa al usuario y se detiene.

Callbacks recibidos por MainWindow via _FrameBridge (thread-safe):
    on_frame(AsciiFrame | None) — None indica error fatal.
    on_status(msg, level)       — mensajes info/warn/error para la UI.
"""
import threading
import time
import cv2

from app.models.ascii_params_model import AsciiParams
from app.models.ascii_frame_model import AsciiFrame
from app.helpers.camera.frame_preprocessor import FramePreprocessor
from app.helpers.ascii.ascii_converter import AsciiConverter
from app.helpers.ascii.ascii_renderer import AsciiRenderer
from typing import Callable

# ── Constantes de apertura ────────────────────────────────────────────────────
_OPEN_TIMEOUT     = 2.5  # Segundos máximos para que cv2.VideoCapture() abra el device.
                          # Necesario porque DSHOW/MSMF pueden bloquearse indefinidamente
                          # con drivers colgados; la apertura corre en hilo con join(timeout).
_MAX_OPEN_RETRIES = 3    # Intentos de apertura antes de declarar el índice inaccesible.

# ── Constantes de reconexión ──────────────────────────────────────────────────
_MAX_CONSECUTIVE_FAILURES = 10   # Frames fallidos (ret=False) consecutivos antes de
                                  # intentar reabrir la cámara. Un valor bajo causaría
                                  # reconexiones por drops momentáneos de USB; 10 filtra
                                  # ruido sin demorar demasiado la detección de cortes reales.
_RECONNECT_DELAY          = 1.5  # Segundos de espera entre reconexiones para dar tiempo
                                  # al driver de liberar el device anterior.
_MAX_RECONNECT_TOTAL      = 3    # Reconexiones máximas por sesión. Tras este límite se
                                  # muestra "desconecta y reconecta el USB" y se detiene,
                                  # evitando el bucle infinito cuando la cámara está
                                  # físicamente desconectada (ej. C920 por sobrecalentamiento).

# ── Constantes de detección de lag ────────────────────────────────────────────
_LAG_WINDOW         = 20   # Ventana deslizante (frames) para el promedio de cap.read().
                            # 20 frames = ~0.7 s a 30 fps. Equilibrio entre reactividad
                            # y estabilidad de la medición.
_LAG_THRESHOLD_MULT = 2.5  # Si avg_read > target_interval × 2.5, la cámara tarda más
                            # del doble de lo esperado. Factor empírico para la C920:
                            # a 2.0 hay falsos positivos en cambios de escena bruscos;
                            # a 3.0 la detección llega tarde.
_LAG_WARN_INTERVAL  = 8.0  # Intervalo mínimo (s) entre advertencias de lag consecutivas
                            # para no saturar la UI con mensajes repetidos.


class CameraWorker(threading.Thread):
    """
    Thread daemon que gestiona el ciclo completo de captura ASCII.

    Diseño de concurrencia:
        - Corre como daemon thread: muere automáticamente si el proceso principal termina.
        - _lock protege el acceso a _params, que puede ser modificado desde el hilo
          principal (ParamsController) mientras el worker lee en su loop.
        - _stop_event permite interrumpir _open_with_retries() desde stop(), evitando
          que el worker quede bloqueado en un intento de apertura cuando el usuario
          pulsa Start de nuevo o cierra la app.
        - Los callbacks on_frame/on_status NO son thread-safe por sí solos; deben ser
          envueltos en _FrameBridge (que usa pyqtSignal) para entregar al hilo Qt.
    """

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
            params    : objeto AsciiParams compartido con el hilo principal.
                        Se lee bajo _lock en cada iteración del loop.
            on_frame  : callback(AsciiFrame | None). None indica error fatal.
            on_status : callback(msg, level) para mensajes info/warn/error en la UI.
        """
        super().__init__(daemon=True)
        self._cam_index  = cam_index
        self._params     = params
        self._on_frame   = on_frame
        self._on_status  = on_status or (lambda msg, lvl: None)
        self._running    = False
        self._paused     = False
        self._lock       = threading.Lock()
        self._stop_event = threading.Event()   # interrumpe apertura y retries cuando stop() es llamado

        self._preprocessor = FramePreprocessor()
        self._converter    = AsciiConverter()
        self._renderer     = AsciiRenderer()

    # ── Helpers de estado ────────────────────────────────────────────────────

    def _status(self, msg: str, level: str = "info") -> None:
        print(f"[CAM] {msg}")
        self._on_status(msg, level)

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

    # ── Loop principal ────────────────────────────────────────────────────────

    def run(self) -> None:
        """
        Punto de entrada del thread (llamado por threading.Thread.start()).

        Flujo:
            1. Abrir cámara con retries (DSHOW → MSMF).
            2. Si falla → on_frame(None) y salir.
            3. Loop:
               a. Leer params bajo lock.
               b. Aplicar cambio de resolución si el usuario la modificó.
               c. Medir tiempo de cap.read() para detección de lag.
               d. Si ret=False, incrementar racha de fallos; al llegar a
                  _MAX_CONSECUTIVE_FAILURES intentar reconexión.
               e. Si se superan _MAX_RECONNECT_TOTAL reconexiones → on_frame(None) y salir.
               f. Frame válido: preprocesar → convertir → renderizar → on_frame(frame).
               g. Throttle: dormir el tiempo necesario para respetar FPS sin superar
                  la velocidad real de la cámara (effective_interval).
        """
        cap = self._open_with_retries(self._cam_index)

        if cap is None:
            self._status(
                f"Índice {self._cam_index} no accesible — "
                "verifica que la cámara no esté en uso por otra app",
                "error",
            )
            self._on_frame(None)
            return

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._status(f"Índice {self._cam_index} activo ({w}×{h})")

        self._running        = True
        _current_res         = self._params.resolution
        _fail_streak         = 0
        _reconnect_count     = 0
        _read_times: list    = []   # ms de cada cap.read() para detectar lag
        _last_lag_warn       = 0.0

        while self._running:
            if self._paused:
                time.sleep(0.05)
                continue

            if self._stop_event.is_set():
                break

            # ── Leer params ──────────────────────────────────────────────
            with self._lock:
                params  = self._params
                new_res = params.resolution

            # ── Cambio de resolución en caliente ─────────────────────────
            if new_res != _current_res:
                try:
                    rw, rh = new_res
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  rw)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, rh)
                    _current_res = new_res
                except Exception:
                    pass

            # ── Captura de frame ──────────────────────────────────────────
            t0 = time.monotonic()
            try:
                ret, frame_bgr = cap.read()
            except Exception as e:
                self._status(f"Excepción en cap.read(): {e}", "warn")
                ret, frame_bgr = False, None
            read_ms = (time.monotonic() - t0) * 1000.0

            # ── Manejo de frame fallido ───────────────────────────────────
            if not ret or frame_bgr is None:
                _fail_streak += 1
                if _fail_streak < _MAX_CONSECUTIVE_FAILURES:
                    continue

                # Intentar reconexión
                _reconnect_count += 1
                if _reconnect_count > _MAX_RECONNECT_TOTAL:
                    self._status(
                        "Cámara desconectada — desconecta y vuelve a conectar el cable USB",
                        "error",
                    )
                    self._on_frame(None)
                    cap.release()
                    return

                self._status(
                    f"Stream cortado — reconectando ({_reconnect_count}/{_MAX_RECONNECT_TOTAL})…",
                    "warn",
                )
                cap.release()
                time.sleep(_RECONNECT_DELAY)
                cap = self._open_with_retries(self._cam_index)

                if cap is None:
                    self._status(
                        "Reconexión fallida — desconecta y vuelve a conectar el cable USB",
                        "error",
                    )
                    self._on_frame(None)
                    return

                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self._status(f"Reconectado ({w}×{h})")
                _fail_streak = 0
                continue

            _fail_streak = 0  # frame exitoso → reset racha

            # ── Detección de lag (sobrecarga de la cámara) ────────────────
            _read_times.append(read_ms)
            if len(_read_times) > _LAG_WINDOW:
                _read_times.pop(0)
            if len(_read_times) >= 10:
                avg_ms     = sum(_read_times) / len(_read_times)
                target_ms  = 1000.0 / max(1, params.fps)
                now        = time.monotonic()
                if avg_ms > target_ms * _LAG_THRESHOLD_MULT and now - _last_lag_warn > _LAG_WARN_INTERVAL:
                    self._status(
                        f"Cámara lenta ({avg_ms:.0f} ms/frame) — "
                        "reduce Columnas, FPS o Resolución para evitar desconexión",
                        "warn",
                    )
                    _last_lag_warn = now

            # ── Procesado ASCII ───────────────────────────────────────────
            try:
                gray      = self._preprocessor.to_gray(frame_bgr)
                gray      = self._preprocessor.normalize(gray)
                ascii_str = self._converter.convert(
                    frame=gray,
                    cols=params.cols,
                    invert=params.invert,
                    charset_key=params.charset,
                )
                image_b64 = self._renderer.render_to_base64(
                    ascii_str,
                    params,
                    color_frame=frame_bgr if params.color_mode else None,
                )
                self._on_frame(AsciiFrame(ascii_str=ascii_str, image_b64=image_b64))
            except Exception as e:
                import traceback
                print(f"[CAM] Error procesando frame: {type(e).__name__}: {e}")
                traceback.print_exc()
                # No matar el loop por un frame procesado con error

            # ── Throttle: respetar FPS sin superar la capacidad real ──────
            # effective_interval = max(intervalo_pedido, tiempo_real × 0.9)
            # El factor 0.9 deja un 10 % de margen sobre el tiempo real de lectura
            # para no acumular trabajo pendiente cuando la cámara es lenta, pero
            # sin igualar exactamente el tiempo de lectura (evita deriva acumulativa).
            effective_interval = max(1.0 / max(1, params.fps), read_ms / 1000.0 * 0.9)
            time.sleep(effective_interval)

        cap.release()

    # ── Control ───────────────────────────────────────────────────────────────

    def stop(self) -> None:
        self._running = False
        self._stop_event.set()

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def is_alive(self) -> bool:
        return super().is_alive()
