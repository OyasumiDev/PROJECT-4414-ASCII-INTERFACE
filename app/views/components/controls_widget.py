"""
controls_widget.py — Panel lateral de controles de captura.

Contiene:
    - Selector de fuente: radio "Cámara / Pantalla".
    - Página Cámara : combo de cámaras detectadas + botón de escaneo completo.
    - Página Pantalla: combo de monitores + calidad de reescala + botón
      "Seleccionar región…" (diálogo numérico x/y/w/h).
    - Botones Start / Stop / Pause / Resume.
    - Etiqueta de estado con color según nivel (info / warn / error / run).

La detección de cámaras se ejecuta en un hilo de fondo para no bloquear la UI;
el resultado se entrega al hilo principal via la señal interna `_cameras_ready`.

`start_requested` emite un CaptureRequest (no un int como antes) para poder
transportar la información específica de cada fuente sin parches.
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton,
    QRadioButton, QButtonGroup, QStackedWidget,
)
from PyQt6.QtCore import pyqtSignal

from app.helpers.camera.camera_enumerator import list_cameras_fast, enumerate_cameras
from app.helpers.screen.screen_enumerator import list_monitors
from app.enums.e_source_type import SourceType
from app.models.capture_request_model import CaptureRequest
from app.views.components.region_dialog import RegionDialog


class CameraControlsWidget(QWidget):
    """
    Widget del panel de controles.

    Señales públicas que MainWindow conecta a CaptureController:
        start_requested(CaptureRequest) → arrancar con la fuente elegida.
        stop_requested()                → detener la captura.
        pause_requested()               → pausar la captura.
        resume_requested()              → reanudar la captura.
        detection_started()             → emitida al cambiar de fuente o escanear
                                          cámaras (MainWindow limpia el display).
    """

    start_requested   = pyqtSignal(object)   # CaptureRequest
    stop_requested    = pyqtSignal()
    pause_requested   = pyqtSignal()
    resume_requested  = pyqtSignal()
    detection_started = pyqtSignal()

    # Señal interna para pasar resultados del hilo de detección al hilo principal
    _cameras_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._cameras: list[tuple[int, str]] = []
        self._region: tuple | None = None
        self._build_ui()
        # Conectar señal interna antes del primer escaneo para no perder el resultado
        self._cameras_ready.connect(self._populate_cameras)
        # Escaneo rápido al arrancar (solo PnP, sin abrir cámaras con cv2)
        self._detect_cameras(full_scan=False)
        self._load_monitors()

    # ── Construcción de la UI ────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        layout.addWidget(_header("Controles"))

        # ── Selector de fuente ──────────────────────────────────────────
        src_row = QHBoxLayout()
        self._rb_cam    = QRadioButton("Cámara")
        self._rb_screen = QRadioButton("Pantalla")
        self._rb_cam.setChecked(True)
        self._src_group = QButtonGroup(self)
        self._src_group.addButton(self._rb_cam, 0)
        self._src_group.addButton(self._rb_screen, 1)
        self._rb_cam.toggled.connect(self._on_source_changed)
        src_row.addWidget(self._rb_cam)
        src_row.addWidget(self._rb_screen)
        layout.addLayout(src_row)

        # ── Stack: página cámara (0) / página pantalla (1) ──────────────
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_camera_page())
        self._stack.addWidget(self._build_screen_page())
        layout.addWidget(self._stack)

        # ── Etiqueta de estado ─────────────────────────────────────────
        self._status = QLabel("Detectando cámaras...")
        self._status.setWordWrap(True)
        self._status.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        layout.addWidget(self._status)

        # ── Botones de control ─────────────────────────────────────────
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

    def _build_camera_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        row = QHBoxLayout()
        self._combo = QComboBox()
        self._combo.addItem("Cámara 0", userData=0)
        self._refresh_btn = QPushButton("↺")
        self._refresh_btn.setFixedWidth(32)
        self._refresh_btn.setToolTip("Buscar cámaras")
        self._refresh_btn.clicked.connect(lambda: self._detect_cameras(full_scan=True))
        row.addWidget(self._combo)
        row.addWidget(self._refresh_btn)
        lay.addLayout(row)
        return page

    def _build_screen_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        mon_row = QHBoxLayout()
        self._mon_combo = QComboBox()
        self._mon_combo.addItem("Monitor principal", userData=1)
        self._mon_refresh = QPushButton("↺")
        self._mon_refresh.setFixedWidth(32)
        self._mon_refresh.setToolTip("Actualizar monitores")
        self._mon_refresh.clicked.connect(self._load_monitors)
        mon_row.addWidget(self._mon_combo)
        mon_row.addWidget(self._mon_refresh)
        lay.addLayout(mon_row)

        q_row = QHBoxLayout()
        q_lbl = QLabel("Calidad")
        q_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        self._q_combo = QComboBox()
        for label, q in [("100 %", 1.0), ("75 %", 0.75), ("50 %", 0.5), ("33 %", 0.33)]:
            self._q_combo.addItem(label, userData=q)
        q_row.addWidget(q_lbl)
        q_row.addWidget(self._q_combo)
        lay.addLayout(q_row)

        reg_row = QHBoxLayout()
        self._region_btn = QPushButton("Seleccionar región…")
        self._region_btn.clicked.connect(self._on_pick_region)
        self._region_clear = QPushButton("✕")
        self._region_clear.setFixedWidth(32)
        self._region_clear.setToolTip("Quitar región (capturar el monitor completo)")
        self._region_clear.clicked.connect(self._on_clear_region)
        reg_row.addWidget(self._region_btn)
        reg_row.addWidget(self._region_clear)
        lay.addLayout(reg_row)

        self._region_lbl = QLabel("Región: monitor completo")
        self._region_lbl.setStyleSheet("color: #888; font-size: 11px;")
        lay.addWidget(self._region_lbl)
        return page

    # ── Fuente activa ───────────────────────────────────────────────────

    def _current_source(self) -> SourceType:
        return SourceType.SCREEN if self._rb_screen.isChecked() else SourceType.CAMERA

    def _on_source_changed(self, _checked=False):
        is_cam = self._rb_cam.isChecked()
        self._stack.setCurrentIndex(0 if is_cam else 1)
        self.detection_started.emit()  # MainWindow limpia el display
        if is_cam:
            self.set_status(self._combo.currentText() or "Cámara", "info")
        else:
            self.set_status("Fuente: pantalla de escritorio", "info")

    # ── Detección de cámaras ───────────────────────────────────────────

    def _detect_cameras(self, full_scan: bool):
        """Lanza la detección de cámaras en un hilo de fondo."""
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
            self._cameras_ready.emit(cameras)

        threading.Thread(target=_run, daemon=True).start()

    def _populate_cameras(self, cameras: list):
        """Rellena el combo con los dispositivos detectados (hilo principal)."""
        self._cameras = cameras
        self._combo.clear()
        for idx, name in cameras:
            self._combo.addItem(name, userData=idx)
        self._refresh_btn.setEnabled(True)
        if self._current_source() == SourceType.CAMERA:
            first = cameras[0][1] if cameras else "Cámara 0"
            self._status.setText(first)
            self._status.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")

    # ── Monitores ──────────────────────────────────────────────────────

    def _load_monitors(self):
        try:
            mons = list_monitors()
        except Exception:
            mons = [(1, "Monitor principal")]
        current = self._mon_combo.currentData()
        self._mon_combo.clear()
        for idx, label in mons:
            self._mon_combo.addItem(label, userData=idx)
        if current is not None:
            pos = self._mon_combo.findData(current)
            if pos >= 0:
                self._mon_combo.setCurrentIndex(pos)

    # ── Región ─────────────────────────────────────────────────────────

    def _on_pick_region(self):
        dlg = RegionDialog(self, initial=self._region)
        if dlg.exec():
            self._region = dlg.region()
            x, y, w, h = self._region
            self._region_lbl.setText(f"Región: {w}×{h} @ ({x}, {y})")

    def _on_clear_region(self):
        self._region = None
        self._region_lbl.setText("Región: monitor completo")

    # ── Start ──────────────────────────────────────────────────────────

    def _on_start(self):
        if self._current_source() == SourceType.SCREEN:
            mon_data = self._mon_combo.currentData()
            mon_idx  = int(mon_data) if mon_data is not None else 1
            q_data   = self._q_combo.currentData()
            quality  = float(q_data) if q_data is not None else 1.0
            req = CaptureRequest(
                source_type=SourceType.SCREEN,
                monitor_index=mon_idx,
                region=self._region,
                quality=quality,
            )
            if self._region:
                x, y, w, h = self._region
                self.set_status(f"▶  Pantalla — región {w}×{h}", "run")
            else:
                self.set_status(f"▶  Pantalla — {self._mon_combo.currentText()}", "run")
                # Aviso: capturar el monitor completo donde vive la app produce
                # efecto "espejo infinito". Sólo advertimos (el worker no conoce
                # la geometría de la ventana Qt).
                self._status.setToolTip(
                    "Si esta ventana queda dentro de la captura verás un efecto "
                    "espejo infinito. Minimiza PROJECT 4414 o define una región."
                )
        else:
            data = self._combo.currentData()
            idx  = int(data) if data is not None else 0
            req  = CaptureRequest(source_type=SourceType.CAMERA, cam_index=idx)
            self.set_status(f"▶  {self._combo.currentText()}", "run")

        self.start_requested.emit(req)

    # ── Estado ─────────────────────────────────────────────────────────

    def set_status(self, message: str, level: str = "info") -> None:
        """
        Actualiza la etiqueta de estado con color según el nivel.

        level: "info" (gris) | "warn" (amarillo) | "error" (rojo) | "run" (verde).
        """
        _colors = {"info": "#888", "warn": "#ffb300", "error": "#ef5350", "run": "#4caf50"}
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
