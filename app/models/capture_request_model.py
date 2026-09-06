"""
capture_request_model.py — Petición de arranque de captura.

Objeto de valor que viaja desde la UI (CameraControlsWidget.start_requested)
hasta CaptureController.start(). Agrupa todo lo necesario para construir el
worker adecuado sin acoplar la vista al controlador.
"""

from dataclasses import dataclass

from app.enums.e_source_type import SourceType


@dataclass
class CaptureRequest:
    """Parámetros de la fuente a arrancar."""

    source_type: SourceType = SourceType.CAMERA

    # ── Cámara ──────────────────────────────────────────────────────────
    cam_index: int = 0

    # ── Pantalla ────────────────────────────────────────────────────────
    monitor_index: int = 1              # índice de mss.monitors (0 = todos)
    region: tuple | None = None         # (x, y, w, h) o None = monitor completo
    quality: float = 1.0               # factor de reescala 0.1–1.0
