"""
params_widget.py — Panel lateral de parámetros de conversión ASCII.

Expone al usuario los controles para ajustar en tiempo real:
    - Columnas      : densidad horizontal del arte ASCII (20–300).
    - FPS target    : frecuencia de captura deseada (1–120).
    - Tamaño fuente : tamaño en px de la fuente monoespaciada (4–24).
    - Resolución    : 480p / 720p / 1080p.
    - Charset       : juego de caracteres ASCII a usar.
    - Invertir      : invierte la paleta (útil con fondo blanco).
    - Modo color    : cada carácter toma el color real del píxel.

Todos los cambios se aplican en tiempo real sin reiniciar la cámara,
llamando directamente a ParamsController.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QCheckBox,
)
from PyQt6.QtCore import Qt

from app.controllers.params_controller import ParamsController
from app.enums.e_charset import CharSet


class ParamsWidget(QWidget):
    """Widget del panel de parámetros ASCII. Recibe un ParamsController ya instanciado."""

    def __init__(self, controller: ParamsController):
        super().__init__()
        self._ctrl = controller
        self._build_ui()

    def _build_ui(self):
        p = self._ctrl.params
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(_header("Parámetros"))

        layout.addWidget(_labeled_slider(
            "Columnas", 20, 300, p.cols,
            lambda v: self._ctrl.set_cols(v),
        ))
        layout.addWidget(_labeled_slider(
            "FPS target", 1, 120, p.fps,
            lambda v: self._ctrl.set_fps(v),
        ))
        layout.addWidget(_labeled_slider(
            "Tamaño fuente", 4, 24, p.font_size,
            lambda v: self._ctrl.set_font_size(v),
        ))

        charset_lbl = QLabel("Charset")
        charset_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        charset_combo = QComboBox()
        for member in CharSet:
            if member.value:
                charset_combo.addItem(member.name)
        idx = charset_combo.findText(p.charset)
        if idx >= 0:
            charset_combo.setCurrentIndex(idx)
        charset_combo.currentTextChanged.connect(self._ctrl.set_charset)
        layout.addWidget(charset_lbl)
        layout.addWidget(charset_combo)

        res_lbl = QLabel("Resolución")
        res_lbl.setStyleSheet("color: #aaa; font-size: 12px;")
        res_combo = QComboBox()
        _resolutions = [("480p  (640×480)", 640, 480), ("720p  (1280×720)", 1280, 720), ("1080p (1920×1080)", 1920, 1080)]
        for label, w, h in _resolutions:
            res_combo.addItem(label, userData=(w, h))
        cur_res = p.resolution
        for i, (_, w, h) in enumerate(_resolutions):
            if (w, h) == cur_res:
                res_combo.setCurrentIndex(i)
                break
        res_combo.currentIndexChanged.connect(
            lambda _: self._ctrl.set_resolution(*res_combo.currentData())
        )
        layout.addWidget(res_lbl)
        layout.addWidget(res_combo)

        invert_chk = QCheckBox("Invertir")
        invert_chk.setChecked(p.invert)
        invert_chk.toggled.connect(self._ctrl.set_invert)
        layout.addWidget(invert_chk)

        color_chk = QCheckBox("Modo color")
        color_chk.setChecked(p.color_mode)
        color_chk.toggled.connect(self._ctrl.set_color_mode)
        layout.addWidget(color_chk)

        layout.addStretch()


def _header(text: str) -> QLabel:
    """Crea un QLabel estilizado como título de sección en el sidebar."""
    lbl = QLabel(text)
    lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #ffffff;")
    return lbl


def _labeled_slider(label: str, min_v: int, max_v: int, value: int, on_change) -> QWidget:
    """
    Crea un widget compuesto que muestra un slider horizontal con etiqueta y valor actual.

    Estructura visual:
        [label]          [valor actual]
        [====slider====]

    El valor numérico se actualiza en tiempo real mientras el usuario arrastra.
    Llama a `on_change(v)` cada vez que el valor cambia.

    Args:
        label    : texto descriptivo que aparece a la izquierda.
        min_v    : valor mínimo del slider.
        max_v    : valor máximo del slider.
        value    : valor inicial.
        on_change: callback(int) que recibe el nuevo valor.

    Returns:
        QWidget contenedor listo para insertar en un layout.
    """
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    val_label = QLabel(str(value))
    val_label.setStyleSheet("color: #e0e0e0; font-size: 12px;")
    val_label.setAlignment(Qt.AlignmentFlag.AlignRight)

    title_row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setStyleSheet("color: #aaa; font-size: 12px;")
    title_row.addWidget(lbl)
    title_row.addWidget(val_label)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(min_v)
    slider.setMaximum(max_v)
    slider.setValue(value)

    def _on_change(v):
        val_label.setText(str(v))
        on_change(v)

    slider.valueChanged.connect(_on_change)

    layout.addLayout(title_row)
    layout.addWidget(slider)
    return container
