"""
region_dialog.py — Diálogo para definir una región de captura de pantalla.

Decisión de diseño: selector NUMÉRICO simple (x, y, ancho, alto) en coordenadas
del escritorio virtual, en lugar de un selector visual arrastrable. Un overlay
transparente a pantalla completa con arrastre de rectángulo es bastante más
código y frágil entre plataformas; para esta pasada, los inputs numéricos son
robustos y suficientes. Los rangos se limitan a la geometría virtual real.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox, QLabel, QPushButton,
)
from PyQt6.QtGui import QGuiApplication


class RegionDialog(QDialog):
    """Devuelve una tupla (x, y, w, h) vía region() cuando se acepta."""

    def __init__(self, parent=None, initial: tuple | None = None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar región de pantalla")
        self.setModal(True)

        screen = QGuiApplication.primaryScreen()
        vg = screen.virtualGeometry()
        self._vg = vg
        max_w, max_h = vg.width(), vg.height()

        if initial and len(initial) == 4:
            x0, y0, w0, h0 = (int(v) for v in initial)
        else:
            x0, y0 = vg.left(), vg.top()
            w0, h0 = min(1280, max_w), min(720, max_h)

        self._x = _spin(vg.left(), vg.left() + max_w, x0)
        self._y = _spin(vg.top(),  vg.top() + max_h, y0)
        self._w = _spin(1, max_w, w0)
        self._h = _spin(1, max_h, h0)

        form = QFormLayout()
        form.addRow("X", self._x)
        form.addRow("Y", self._y)
        form.addRow("Ancho", self._w)
        form.addRow("Alto", self._h)

        full_btn = QPushButton("Usar pantalla completa")
        full_btn.clicked.connect(self._fill_full)

        info = QLabel(f"Escritorio virtual: {max_w}×{max_h} (origen {vg.left()}, {vg.top()})")
        info.setStyleSheet("color:#888; font-size:11px;")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(full_btn)
        lay.addWidget(info)
        lay.addWidget(buttons)

    def _fill_full(self):
        self._x.setValue(self._vg.left())
        self._y.setValue(self._vg.top())
        self._w.setValue(self._vg.width())
        self._h.setValue(self._vg.height())

    def region(self) -> tuple[int, int, int, int]:
        return (self._x.value(), self._y.value(), self._w.value(), self._h.value())


def _spin(lo: int, hi: int, val: int) -> QSpinBox:
    s = QSpinBox()
    s.setRange(int(lo), int(hi))
    s.setValue(int(max(lo, min(val, hi))))
    s.setSingleStep(10)
    return s
