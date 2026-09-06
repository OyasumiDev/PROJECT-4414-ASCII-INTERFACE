"""
screen_worker.py — Worker de captura de PANTALLA DE ESCRITORIO → ASCII.

Implementa los hooks de BaseCaptureWorker sobre la librería `mss`, bastante más
rápida que PIL.ImageGrab para captura repetida en un loop.

Fuente configurable:
    - Monitor completo   → índice de mss.monitors (0 = todos los monitores juntos,
                           1..N = cada monitor físico).
    - Región arbitraria  → (x, y, width, height) en coordenadas del escritorio
                           virtual. Si se define, tiene prioridad sobre el monitor.

Rendimiento:
    - `quality` (0.1 ≤ q ≤ 1.0) reescala el frame capturado con INTER_AREA ANTES
      de entrar al pipeline; a 1080p completo bajarlo a 0.5 reduce ~4× el coste.
    - Además, aunque quality sea 1.0, si el ancho capturado supera
      _MAX_CAPTURE_WIDTH se aplica un downscale de seguridad para no saturar el
      renderer PIL con imágenes enormes (decisión: proteger el pipeline siempre).

Concurrencia:
    - Las instancias de mss NO son thread-safe y deben usarse en el hilo que las
      creó. Por eso el objeto mss se crea dentro de _setup(), que ya corre en el
      hilo del worker (no en __init__, que corre en el hilo principal).

Aviso de auto-captura:
    - Si el usuario captura el monitor completo donde está la ventana de la app,
      verá un efecto "espejo infinito". El worker no conoce la geometría de la
      ventana Qt, así que el aviso se muestra desde la UI (controls_widget) antes
      de arrancar; aquí sólo se documenta.
"""
import numpy as np
import cv2
from typing import Callable

from app.helpers.capture.base_capture_worker import BaseCaptureWorker
from app.models.ascii_params_model import AsciiParams


def _new_mss():
    """Instancia mss compatible con 9.x (`mss.mss`) y 10.x (`mss.MSS`)."""
    import mss
    factory = getattr(mss, "MSS", None) or getattr(mss, "mss")
    return factory()


# Downscale de seguridad por encima de este ancho, aun con quality == 1.0.
# 2560 deja pasar 1080p y 1440p a resolución nativa (máximo detalle ASCII);
# sólo recorta pantallas 4K, donde el coste sí se dispara.
_MAX_CAPTURE_WIDTH = 2560


class ScreenWorker(BaseCaptureWorker):
    """
    Worker de captura de pantalla. Hereda de BaseCaptureWorker todo el ciclo
    de vida; sólo aporta la obtención del frame vía mss.

    La captura de pantalla casi nunca "falla" devolviendo None (los errores de
    mss son excepciones), por eso se afloja la reconexión respecto a la cámara:
        RECONNECT_DELAY     = 0.5
        MAX_RECONNECT_TOTAL = 5
    """

    SOURCE_TAG          = "SCR"
    RECONNECT_DELAY     = 0.5
    MAX_RECONNECT_TOTAL = 5

    def __init__(
        self,
        params: AsciiParams,
        on_frame: Callable,
        on_status: Callable[[str, str], None] | None = None,
        monitor_index: int = 1,
        region: tuple | None = None,
        quality: float = 1.0,
    ):
        """
        Args:
            params        : AsciiParams compartido (leído bajo lock en el loop base).
            on_frame      : callback(AsciiFrame | None). None = error fatal.
            on_status     : callback(msg, level) para la UI.
            monitor_index : índice de mss.monitors a capturar si region es None.
            region        : (x, y, w, h) en coords del escritorio virtual, o None.
            quality       : factor de reescala 0.1–1.0 aplicado antes del pipeline.
        """
        super().__init__(params, on_frame, on_status)
        self._monitor_index = int(monitor_index)
        self._region        = tuple(region) if region else None
        self._quality       = max(0.1, min(float(quality), 1.0))
        self._sct           = None
        self._bbox: dict | None = None   # dict {left, top, width, height} para sct.grab()

    # ── Mensajes específicos de pantalla ─────────────────────────────────

    def _msg_reconnecting(self, count: int, total: int) -> str:
        return f"Captura de pantalla interrumpida — reintentando ({count}/{total})…"

    def _msg_reconnect_failed(self) -> str:
        return "No se pudo reanudar la captura de pantalla"

    def _msg_fatal_disconnect(self) -> str:
        return "Captura de pantalla no disponible — revisa el monitor o la región"

    def _msg_lag(self, avg_ms: float) -> str:
        return (
            f"Captura de pantalla lenta ({avg_ms:.0f} ms/frame) — "
            "reduce Columnas, FPS o Calidad"
        )

    # ── Hooks de BaseCaptureWorker ───────────────────────────────────────

    def _setup(self) -> bool:
        try:
            import mss  # noqa: F401
        except ImportError:
            self._status("Falta la librería 'mss' — ejecuta: pip install mss", "error")
            return False

        try:
            if self._sct is not None:
                try:
                    self._sct.close()
                except Exception:
                    pass
            self._sct = _new_mss()
            monitors = self._sct.monitors  # [0] = virtual (todos), [1..] = físicos

            if self._region is not None:
                x, y, w, h = self._region
                if int(w) <= 0 or int(h) <= 0:
                    self._status("Región inválida (ancho/alto ≤ 0)", "error")
                    return False
                self._bbox = {
                    "left": int(x), "top": int(y),
                    "width": int(w), "height": int(h),
                }
                label = f"región {int(w)}×{int(h)} @ ({int(x)}, {int(y)})"
            else:
                idx = self._monitor_index
                if idx < 0 or idx >= len(monitors):
                    idx = 1 if len(monitors) > 1 else 0
                self._monitor_index = idx
                m = monitors[idx]
                self._bbox = {
                    "left": int(m["left"]), "top": int(m["top"]),
                    "width": int(m["width"]), "height": int(m["height"]),
                }
                who = "todos los monitores" if idx == 0 else f"monitor {idx}"
                label = f"{who} {int(m['width'])}×{int(m['height'])}"

            # Probe: un grab de verificación
            probe = np.asarray(self._sct.grab(self._bbox))
            if probe.ndim != 3 or probe.shape[2] < 3:
                self._status("La captura de pantalla no devolvió una imagen válida", "error")
                return False

            extra = "" if self._quality >= 1.0 else f" · calidad {int(self._quality * 100)}%"
            self._status(f"Pantalla activa — {label}{extra}", "info")
            return True

        except Exception as e:
            self._status(f"No se pudo iniciar la captura de pantalla: {e}", "error")
            return False

    def _read_frame(self) -> tuple[bool, "any"]:
        raw = self._sct.grab(self._bbox)
        img = np.asarray(raw)                       # BGRA, shape (h, w, 4)
        if img.ndim != 3 or img.shape[2] < 3:
            return False, None
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        h, w = frame.shape[:2]
        scale = self._quality
        if scale >= 1.0 and w > _MAX_CAPTURE_WIDTH:
            scale = _MAX_CAPTURE_WIDTH / float(w)   # downscale de seguridad
        if scale < 1.0:
            frame = cv2.resize(
                frame,
                (max(1, int(w * scale)), max(1, int(h * scale))),
                interpolation=cv2.INTER_AREA,
            )
        return True, frame

    def _teardown(self) -> None:
        if self._sct is not None:
            try:
                self._sct.close()
            except Exception:
                pass
            self._sct = None
