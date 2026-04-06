"""
app_state.py — Estado global centralizado de la aplicación (Singleton).

AppState es el único punto de verdad compartido entre controllers y workers.
Al ser Singleton (via SingletonMeta), todos los módulos que instancien
`AppState()` obtienen exactamente el mismo objeto, lo que garantiza coherencia
sin pasar referencias explícitas por toda la cadena de llamadas.

Contiene:
    - params          : parámetros actuales de conversión ASCII (cols, fps, etc.)
    - camera_state    : estado del ciclo de vida de la cámara (IDLE/RUNNING/…)
    - current_cam_index: índice cv2 de la cámara seleccionada actualmente
"""

from app.core.patterns.singleton import SingletonMeta
from app.models.ascii_params_model import AsciiParams
from app.enums.e_camera_state import CameraState


class AppState(metaclass=SingletonMeta):
    """
    Contenedor Singleton del estado mutable de la aplicación.

    No usar directamente para emitir señales Qt; para eso existe _FrameBridge
    en main_window.py. AppState solo almacena datos, no sabe nada de la UI.
    """

    def __init__(self):
        # Parámetros de conversión ASCII (cols, fps, charset, color_mode, etc.)
        self.params: AsciiParams = AsciiParams()

        # Estado del ciclo de vida de la cámara
        self.camera_state: CameraState = CameraState.IDLE

        # Índice cv2 de la cámara activa (0, 1, 2…)
        self.current_cam_index: int = 0
