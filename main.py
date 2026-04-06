"""
main.py — Punto de entrada de la aplicación ASCII Cam.

Crea la QApplication, aplica el icono personalizado (Icon.ico) tanto a nivel
de ventana como en la barra de tareas de Windows (via AppUserModelID),
instancia MainWindow y arranca el event loop de Qt.
"""
import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.views.main_window import MainWindow

_ICON = Path(__file__).parent / "assets" / "icons" / "ROJECT 4414 \u2014 ASCII Galaxy ICON.ico"

# Registrar App User Model ID para que Windows muestre el icono correcto en la taskbar
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AsciiCam.App")
except Exception:
    pass


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if _ICON.exists():
        icon = QIcon(str(_ICON))
        app.setWindowIcon(icon)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


main()
