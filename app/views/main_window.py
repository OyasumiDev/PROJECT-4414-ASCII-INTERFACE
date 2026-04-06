"""
main_window.py — Ventana principal de ASCII Cam.

Responsabilidades:
    - Construir el layout: display ASCII (izquierda) + sidebar scrollable (derecha).
    - Instanciar y conectar CameraController y ParamsController.
    - Albergar _FrameBridge, el puente thread-safe entre el worker de cámara
      (hilo de fondo) y los widgets Qt (hilo principal).
    - Propagar mensajes de estado/error del worker a la UI via señales Qt.
    - Aplicar el stylesheet global de la aplicación (_STYLE).
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor

from app.config.config import APP_TITLE, APP_WIDTH, APP_HEIGHT
from app.controllers.camera_controller import CameraController
from app.controllers.params_controller import ParamsController
from app.models.ascii_frame_model import AsciiFrame
from app.views.components.display_widget import AsciiDisplayWidget
from app.views.components.controls_widget import CameraControlsWidget
from app.views.components.params_widget import ParamsWidget

_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
}
QComboBox, QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
    min-height: 24px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #444;
    selection-background-color: #2e7d32;
    color: #e0e0e0;
}
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
    min-height: 28px;
}
QPushButton:hover  { background-color: #383838; border-color: #666; }
QPushButton:pressed { background-color: #1a1a1a; }
QPushButton#start_btn { background-color: #1b5e20; border-color: #2e7d32; }
QPushButton#start_btn:hover { background-color: #2e7d32; }
QPushButton#stop_btn  { background-color: #7f0000; border-color: #b71c1c; }
QPushButton#stop_btn:hover  { background-color: #b71c1c; }
QSlider::groove:horizontal {
    background: #444;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #4caf50;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal { background: #4caf50; border-radius: 2px; }
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555;
    border-radius: 3px;
    background: #2d2d2d;
}
QCheckBox::indicator:checked { background-color: #4caf50; border-color: #4caf50; }
QScrollArea  { border: none; background: transparent; }
QScrollBar:vertical {
    background: #1e1e1e;
    width: 8px;
}
QScrollBar::handle:vertical { background: #444; border-radius: 4px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QFrame[frameShape="4"] { color: #333; }
QLabel { background: transparent; }
QStatusBar { color: #888; font-size: 11px; }
"""


class _FrameBridge(QObject):
    """Puente thread-safe: recibe callbacks del worker thread, emite señales Qt en el hilo principal."""
    frame_ready = pyqtSignal(object)         # AsciiFrame
    cam_error   = pyqtSignal()
    cam_status  = pyqtSignal(str, str)       # (mensaje, nivel: info/warn/error)

    def on_frame(self, frame: AsciiFrame | None) -> None:
        if frame is None:
            self.cam_error.emit()
        else:
            self.frame_ready.emit(frame)

    def on_status(self, msg: str, level: str) -> None:
        self.cam_status.emit(msg, level)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.

    Orquesta la UI completa:
        - _display   : AsciiDisplayWidget — muestra el frame ASCII renderizado.
        - _controls  : CameraControlsWidget — selector de cámara y botones.
        - _params_w  : ParamsWidget — sliders y opciones de conversión.
        - _bridge    : _FrameBridge — recibe callbacks del worker y emite señales Qt.
        - _camera    : CameraController — gestiona el ciclo de vida del worker.
        - _params    : ParamsController — aplica cambios de parámetros en tiempo real.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(APP_WIDTH, APP_HEIGHT)
        self.setStyleSheet(_STYLE)

        self._bridge  = _FrameBridge()
        self._params  = ParamsController()
        self._camera  = CameraController(
            on_frame=self._bridge.on_frame,
            on_status=self._bridge.on_status,
        )

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self._display  = AsciiDisplayWidget()
        self._controls = CameraControlsWidget()
        self._params_w = ParamsWidget(self._params)

        # Sidebar: controls + divider + params, scrollable
        sidebar_inner = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_inner)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(12)
        sidebar_layout.addWidget(self._controls)
        sidebar_layout.addWidget(_divider())
        sidebar_layout.addWidget(self._params_w)
        sidebar_layout.addStretch()

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidget(sidebar_inner)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFixedWidth(290)
        sidebar_scroll.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._display)
        root_layout.addWidget(sidebar_scroll)

        self.setCentralWidget(root)
        self.statusBar().showMessage("Listo")

    def _connect_signals(self):
        """
        Conecta todas las señales Qt entre componentes.

        Flujo de frames:
            CameraWorker → _FrameBridge.on_frame() → frame_ready → _display.set_frame()

        Flujo de controles:
            _controls.start_requested → _camera.start()
            _controls.stop_requested  → _camera.stop() + _display.clear_frame()

        Flujo de estado/error:
            _FrameBridge.cam_error  → _on_cam_error()
            _FrameBridge.cam_status → _on_cam_status() → statusBar + _controls
        """
        # Frame bridge → display
        self._bridge.frame_ready.connect(
            lambda frame: self._display.set_frame(frame.image_b64)
        )
        self._bridge.cam_error.connect(self._on_cam_error)
        self._bridge.cam_status.connect(self._on_cam_status)

        # Controls → camera controller
        self._controls.start_requested.connect(self._camera.start)
        self._controls.stop_requested.connect(self._camera.stop)
        self._controls.pause_requested.connect(self._camera.pause)
        self._controls.resume_requested.connect(self._camera.resume)

        # Stop y búsqueda de cámaras → limpiar display (eliminar último frame mostrado)
        self._controls.stop_requested.connect(self._display.clear_frame)
        self._controls.detection_started.connect(self._display.clear_frame)

    def _on_cam_error(self):
        """Muestra error fatal en la etiqueta de estado del sidebar."""
        self._controls.set_status("Cámara no accesible", "error")

    def _on_cam_status(self, msg: str, level: str) -> None:
        """
        Propaga un mensaje de estado del worker a la UI.

        Actualiza tanto la statusBar inferior como la etiqueta del sidebar,
        usando colores distintos según el nivel (info/warn/error).
        """
        self.statusBar().showMessage(msg)
        self._controls.set_status(msg, level)

    def closeEvent(self, event):
        self._camera.stop()
        super().closeEvent(event)


def _divider() -> QFrame:
    """Crea una línea horizontal separadora para el sidebar."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    return line
