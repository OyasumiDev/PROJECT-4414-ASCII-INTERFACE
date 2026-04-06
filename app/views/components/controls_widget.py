"""
controls_widget.py — Panel lateral de controles de cámara.

Contiene:
    - Combo para seleccionar la cámara detectada en el sistema.
    - Botón de refresco que lanza un escaneo completo de dispositivos.
    - Botones Start / Stop / Pause / Resume.
    - Etiqueta de estado que muestra info, advertencias y errores en color.

La detección de cámaras se ejecuta en un hilo de fondo para no bloquear la UI;
el resultado se entrega al hilo principal via la señal interna `_cameras_ready`.
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
)
from PyQt6.QtCore import pyqtSignal

from app.helpers.camera.camera_enumerator import list_cameras_fast, enumerate_cameras


class CameraControlsWidget(QWidget):
    """
    Widget del panel de controles de cámara.

    Señales públicas que MainWindow conecta a CameraController:
        start_requested(int)  → índice cv2 de la cámara seleccionada.
        stop_requested()      → detener la captura.
        pause_requested()     → pausar la captura.
        resume_requested()    → reanudar la captura.
        detection_started()   → emitida al iniciar búsqueda de cámaras (limpia display).
    """

    start_requested   = pyqtSignal(int)   # cam_index
    stop_requested    = pyqtSignal()
    pause_requested   = pyqtSignal()
    resume_requested  = pyqtSignal()
    detection_started = pyqtSignal()      # cámara en búsqueda

    # Señal interna para pasar resultados del hilo de detección al hilo principal
    _cameras_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._cameras: list[tuple[int, str]] = []
        self._build_ui()
        # Conectar señal interna antes del primer escaneo para no perder el resultado
        self._cameras_ready.connect(self._populate_cameras)
        # Escaneo rápido al arrancar (solo PnP, sin abrir cámaras con cv2)
        self._detect_cameras(full_scan=False)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        layout.addWidget(_header("Controles"))

        cam_row = QHBoxLayout()
        self._combo = QComboBox()
        self._combo.addItem("Cámara 0", userData=0)
        self._refresh_btn = QPushButton("↺")
        self._refresh_btn.setFixedWidth(32)
        self._refresh_btn.setToolTip("Buscar cámaras")
        self._refresh_btn.clicked.connect(lambda: self._detect_cameras(full_scan=True))
        cam_row.addWidget(self._combo)
        cam_row.addWidget(self._refresh_btn)
        layout.addLayout(cam_row)

        self._status = QLabel("Detectando cámaras...")
        self._status.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        layout.addWidget(self._status)

        btn_row1 = QHBoxLayout()
        self._start_btn = QPushButton("▶  Start")
        self._start_btn.setObjectName("start_btn")
        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn = QPushButton("■  Stop")
        self._stop_btn.setObjectName("stop_btn")
        self._stop_btn.clicked.connect(self.stop_requested)
        btn_row1.addWidget(self._start_btn)
        btn_row1.addWidget(self._stop_btn)
        layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        pause_btn  = QPushButton("⏸  Pause")
        resume_btn = QPushButton("▶▶  Resume")
        pause_btn.clicked.connect(self.pause_requested)
        resume_btn.clicked.connect(self.resume_requested)
        btn_row2.addWidget(pause_btn)
        btn_row2.addWidget(resume_btn)
        layout.addLayout(btn_row2)

    def _on_start(self):
        idx = self._combo.currentData() if self._combo.currentData() is not None else 0
        name = self._combo.currentText()
        self._status.setText(f"▶  {name}")
        self._status.setStyleSheet("color: #4caf50; font-style: normal; font-size: 11px;")
        self.start_requested.emit(idx)

    def _detect_cameras(self, full_scan: bool):
        """
        Lanza la detección de cámaras en un hilo de fondo.

        Args:
            full_scan: si True, abre cada índice con cv2 para confirmar que
                       funciona (más lento, para el botón Refresh).
                       Si False, usa solo la consulta PnP de Windows (rápido,
                       para el arranque inicial).
        """
        self._refresh_btn.setEnabled(False)
        self._status.setText("Buscando cámaras...")
        self._status.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        self.detection_started.emit()

        def _run():
            try:
                cameras = enumerate_cameras() if full_scan else list_cameras_fast()
            except Exception:
                cameras = []
            if not cameras:
                cameras = [(0, "Cámara 0")]
            # Emitir desde el hilo de fondo; Qt entregará la señal en el hilo principal
            self._cameras_ready.emit(cameras)

        threading.Thread(target=_run, daemon=True).start()

    def _populate_cameras(self, cameras: list):
        """
        Rellena el combo con los dispositivos detectados.
        Siempre se ejecuta en el hilo principal (vía señal Qt).
        """
        self._cameras = cameras
        self._combo.clear()
        for idx, name in cameras:
            self._combo.addItem(name, userData=idx)
        first = cameras[0][1] if cameras else "Cámara 0"
        self._status.setText(first)
        self._status.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        self._refresh_btn.setEnabled(True)

    def set_status(self, message: str, level: str = "info") -> None:
        """
        Actualiza la etiqueta de estado con color según el nivel.

        Args:
            message: texto a mostrar.
            level:   "info" (gris) | "warn" (amarillo) | "error" (rojo).
        """
        _colors = {"info": "#888", "warn": "#ffb300", "error": "#ef5350"}
        color = _colors.get(level, "#888")
        self._status.setText(message)
        self._status.setStyleSheet(f"color: {color}; font-style: normal; font-size: 11px;")

    def set_error(self, message: str):
        """Atajo para mostrar un mensaje de error en la etiqueta de estado."""
        self.set_status(f"Error: {message}", "error")


def _header(text: str) -> QLabel:
    """Crea un QLabel estilizado como título de sección en el sidebar."""
    lbl = QLabel(text)
    lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #ffffff;")
    return lbl
