"""
e_camera_state.py — Enum de estados del ciclo de vida de la cámara.

Define los cuatro estados posibles por los que pasa una sesión de captura.
CameraController y AppState usan este enum para comunicar el estado actual
a la UI sin acoplar lógica de negocio a cadenas de texto.
"""

from enum import Enum


class CameraState(Enum):
    """
    Estados del ciclo de vida de la cámara.

    IDLE    : ningún worker activo; la cámara no está siendo usada.
    RUNNING : el CameraWorker está capturando y procesando frames.
    PAUSED  : el worker existe pero la captura está suspendida.
    ERROR   : fallo al abrir la cámara o stream cortado sin recuperación.
    """

    IDLE    = "idle"
    RUNNING = "running"
    PAUSED  = "paused"
    ERROR   = "error"
