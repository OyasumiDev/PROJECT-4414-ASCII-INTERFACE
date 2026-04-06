"""
camera_state.py — Gestor del estado del ciclo de vida de la cámara.

Encapsula el valor actual de CameraState y expone métodos convenientes
para leerlo y modificarlo. Se usa desde CameraController para mantener
el estado sincronizado con las acciones del usuario (start/stop/pause).
"""

from app.enums.e_camera_state import CameraState


class CameraStateManager:
    """
    Gestiona las transiciones de estado de la cámara.

    Estados posibles (ver CameraState):
        IDLE    → la cámara no está activa
        RUNNING → capturando y procesando frames
        PAUSED  → captura suspendida temporalmente
        ERROR   → fallo en la apertura o stream cortado
    """

    def __init__(self):
        self._state = CameraState.IDLE

    @property
    def state(self) -> CameraState:
        """Estado actual de la cámara (solo lectura via property)."""
        return self._state

    def set(self, state: CameraState) -> None:
        """Actualiza el estado a un nuevo valor de CameraState."""
        self._state = state

    def is_running(self) -> bool:
        """Devuelve True si la cámara está en estado RUNNING."""
        return self._state == CameraState.RUNNING
