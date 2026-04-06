import base64
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class AsciiDisplayWidget(QLabel):
    """Muestra el frame ASCII como imagen. Thread-safe: llamar set_frame solo desde el hilo principal."""

    def __init__(self):
        super().__init__()
        self._pixmap: QPixmap | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #000000;")
        self.setText("Sin señal — presiona Start")

    def set_frame(self, image_b64: str) -> None:
        data = base64.b64decode(image_b64)
        px = QPixmap()
        px.loadFromData(data)
        self._pixmap = px
        self._repaint()

    def clear_frame(self) -> None:
        self._pixmap = None
        super().setPixmap(QPixmap())
        self.setText("Sin señal — presiona Start")

    def resizeEvent(self, event):
        self._repaint()
        super().resizeEvent(event)

    def _repaint(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)
