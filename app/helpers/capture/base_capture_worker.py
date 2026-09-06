"""
base_capture_worker.py — Clase base para cualquier worker de captura → ASCII.

Extrae toda la lógica que NO depende de la fuente concreta (webcam, pantalla…),
que antes vivía únicamente en CameraWorker:

    - Ciclo de vida del thread daemon: run / stop / pause / resume + _stop_event
      (para interrumpir una apertura o un reintento en curso).
    - Lectura thread-safe de AsciiParams bajo _lock.
    - Throttle de FPS con effective_interval (respeta el FPS pedido sin superar
      la velocidad real de la fuente, con 10 % de margen anti-deriva).
    - Detección de lag por ventana deslizante de _LAG_WINDOW lecturas.
    - Reconexión genérica: tras MAX_CONSECUTIVE_FAILURES fallos seguidos se cierra
      y reabre la fuente, hasta MAX_RECONNECT_TOTAL veces por sesión.
    - Pipeline ASCII compartido: FramePreprocessor → AsciiConverter → AsciiRenderer
      → AsciiFrame → on_frame().

Las subclases sólo implementan los hooks dependientes de la fuente:

    _setup()        -> bool   Abre la fuente. Devuelve True si quedó lista.
                              DEBE emitir su propio _status(...) en éxito y en fallo.
    _read_frame()   -> tuple  (ok: bool, frame_bgr: np.ndarray | None).
                              El frame debe ser BGR uint8 (lo que espera el pipeline).
    _apply_params(params)     Aplica cambios de parámetros en caliente. Opcional.
    _teardown()               Libera los recursos de la fuente. Opcional.

Los mensajes de estado (reconexión, lag, desconexión fatal) son métodos
_msg_* sobreescribibles para que cada fuente use su propia redacción.

Cumple estructuralmente IFrameSource (start viene de threading.Thread).
Los callbacks on_frame / on_status NO son thread-safe por sí solos: deben
envolverse en _FrameBridge (pyqtSignal) para entregarlos al hilo Qt.
"""
import threading
import time
import traceback
from typing import Callable

import cv2

from app.models.ascii_params_model import AsciiParams
from app.models.ascii_frame_model import AsciiFrame
from app.helpers.camera.frame_preprocessor import FramePreprocessor
from app.helpers.ascii.ascii_converter import AsciiConverter
from app.helpers.ascii.ascii_renderer import AsciiRenderer


class BaseCaptureWorker(threading.Thread):
    """Thread daemon con el ciclo completo de captura ASCII. Ver módulo."""

    # ── Tunables (las subclases pueden sobreescribir) ────────────────────────
    SOURCE_TAG               = "CAP"   # prefijo de los logs por consola
    MAX_CONSECUTIVE_FAILURES = 10      # fallos seguidos antes de intentar reabrir
    RECONNECT_DELAY          = 1.5     # segundos de espera entre reaperturas
    MAX_RECONNECT_TOTAL      = 3       # reaperturas máximas por sesión

    _LAG_WINDOW              = 20      # frames en la ventana deslizante de lag
    _LAG_THRESHOLD_MULT      = 1.8     # avg_work > periodo_FPS × este factor ⇒ lag
    _LAG_WARN_INTERVAL       = 10.0    # segundos mínimos entre avisos de lag

    def __init__(
        self,
        params: AsciiParams,
        on_frame: Callable,
        on_status: Callable[[str, str], None] | None = None,
    ):
        super().__init__(daemon=True)
        self._params     = params
        self._on_frame   = on_frame
        self._on_status  = on_status or (lambda msg, lvl: None)
        self._running    = False
        self._paused     = False
        self._lock       = threading.Lock()
        self._stop_event = threading.Event()

        self._preprocessor = FramePreprocessor()
        self._converter    = AsciiConverter()
        self._renderer     = AsciiRenderer()

    # ── Helper de estado ────────────────────────────────────────────────────

    def _status(self, msg: str, level: str = "info") -> None:
        print(f"[{self.SOURCE_TAG}] {msg}")
        self._on_status(msg, level)

    # ── Hooks que implementa la subclase ───────────────────────────────────

    def _setup(self) -> bool:
        """Abre la fuente. True si quedó lista. Debe emitir su propio _status()."""
        raise NotImplementedError

    def _read_frame(self) -> tuple[bool, "any"]:
        """Devuelve (ok, frame_bgr | None). frame_bgr debe ser numpy BGR uint8."""
        raise NotImplementedError

    def _apply_params(self, params: AsciiParams) -> None:
        """Aplica cambios de parámetros en caliente (p. ej. resolución). Opcional."""
        pass

    def _teardown(self) -> None:
        """Libera los recursos de la fuente. Opcional."""
        pass

    # ── Mensajes de estado (sobreescribibles por fuente) ───────────────────

    def _msg_reconnecting(self, count: int, total: int) -> str:
        return f"Señal perdida — reintentando ({count}/{total})…"

    def _msg_reconnect_failed(self) -> str:
        return "No se pudo recuperar la fuente de captura"

    def _msg_fatal_disconnect(self) -> str:
        return "Fuente de captura no disponible"

    def _msg_lag(self, avg_ms: float) -> str:
        return (
            f"Captura lenta ({avg_ms:.0f} ms/frame) — "
            "reduce Columnas, FPS o resolución/calidad"
        )

    # ── Loop principal (template method) ──────────────────────────────────

    def run(self) -> None:
        if not self._setup():
            # _setup() ya emitió el motivo concreto por _status(..., "error")
            self._on_frame(None)
            return

        self._running    = True
        _fail_streak     = 0
        _reconnect_count = 0
        _work_times: list = []
        _last_lag_warn   = 0.0

        while self._running:
            if self._paused:
                time.sleep(0.05)
                continue
            if self._stop_event.is_set():
                break

            _iter_t0 = time.monotonic()

            # ── Leer params bajo lock ───────────────────────────────────
            with self._lock:
                params = self._params

            self._apply_params(params)

            # ── Captura de frame ────────────────────────────────────────
            try:
                ok, frame_bgr = self._read_frame()
            except Exception as e:
                self._status(f"Excepción leyendo frame: {e}", "warn")
                ok, frame_bgr = False, None

            # ── Frame fallido → racha / reconexión ──────────────────────
            if not ok or frame_bgr is None:
                _fail_streak += 1
                if _fail_streak < self.MAX_CONSECUTIVE_FAILURES:
                    continue

                _reconnect_count += 1
                if _reconnect_count > self.MAX_RECONNECT_TOTAL:
                    self._status(self._msg_fatal_disconnect(), "error")
                    self._on_frame(None)
                    self._teardown()
                    return

                self._status(
                    self._msg_reconnecting(_reconnect_count, self.MAX_RECONNECT_TOTAL),
                    "warn",
                )
                self._teardown()
                time.sleep(self.RECONNECT_DELAY)
                if self._stop_event.is_set():
                    break

                if not self._setup():
                    self._status(self._msg_reconnect_failed(), "error")
                    self._on_frame(None)
                    return

                _fail_streak = 0
                continue

            _fail_streak = 0

            # ── Pipeline ASCII ─────────────────────────────────────────
            # Una sola operación toca el frame a resolución completa: el
            # resize a la rejilla (cols × rows). Brillo, gris, CLAHE y el
            # mapeo a caracteres corren ya sobre esa imagen diminuta.
            try:
                h, w = frame_bgr.shape[:2]
                rows = self._converter.rows_for(params.cols, w, h)
                small = cv2.resize(
                    frame_bgr, (params.cols, rows), interpolation=cv2.INTER_AREA
                )
                small = self._preprocessor.apply_brightness(small, params.brightness)

                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                gray = self._preprocessor.normalize(gray)
                grid, chars = self._converter.to_index_grid(
                    gray, params.invert, params.charset
                )
                image_b64 = self._renderer.render_grid_to_base64(
                    grid, chars, params,
                    color_cells=small if params.color_mode else None,
                )
                self._on_frame(AsciiFrame(ascii_str="", image_b64=image_b64))
            except Exception as e:
                print(f"[{self.SOURCE_TAG}] Error procesando frame: {type(e).__name__}: {e}")
                traceback.print_exc()
                # Un frame con error no debe matar el loop.

            # ── Detección de lag (sobre el trabajo TOTAL del frame) ─────
            work_ms = (time.monotonic() - _iter_t0) * 1000.0
            _work_times.append(work_ms)
            if len(_work_times) > self._LAG_WINDOW:
                _work_times.pop(0)
            if len(_work_times) >= 8:
                avg_ms    = sum(_work_times) / len(_work_times)
                target_ms = 1000.0 / max(1, params.fps)
                now       = time.monotonic()
                if (
                    avg_ms > target_ms * self._LAG_THRESHOLD_MULT
                    and now - _last_lag_warn > self._LAG_WARN_INTERVAL
                ):
                    self._status(self._msg_lag(avg_ms), "warn")
                    _last_lag_warn = now

            # ── Throttle: dormir lo que falte para el periodo del FPS ───
            # Si el trabajo ya superó el periodo, se cede un mínimo y se
            # sigue (nunca un busy-loop): así el FPS pedido actúa de tope
            # real y la CPU descansa entre frames.
            period = 1.0 / max(1, params.fps)
            time.sleep(max(0.002, period - (time.monotonic() - _iter_t0)))

        self._teardown()

    # ── Control ───────────────────────────────────────────────────────────

    def stop(self) -> None:
        self._running = False
        self._stop_event.set()

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def is_alive(self) -> bool:
        return super().is_alive()
