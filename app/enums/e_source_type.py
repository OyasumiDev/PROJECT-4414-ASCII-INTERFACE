"""
e_source_type.py — Enum de la fuente de frames activa.

La app puede alimentar el pipeline ASCII desde distintos orígenes. El usuario
elige uno en la UI (radio "Cámara / Pantalla"); CaptureController usa este enum
para instanciar el worker correcto.

    CAMERA : webcam vía cv2.VideoCapture  → CameraWorker
    SCREEN : pantalla de escritorio vía mss → ScreenWorker
"""

from enum import Enum


class SourceType(Enum):
    """Orígenes posibles para el feed de frames."""

    CAMERA = "camera"
    SCREEN = "screen"
