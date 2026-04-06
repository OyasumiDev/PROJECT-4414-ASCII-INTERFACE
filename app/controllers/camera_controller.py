"""
camera_controller.py
Orquesta el ciclo de vida de la cámara:
  - inicia / detiene / pausa CameraWorker
  - actualiza CameraState en AppState
  - recibe frames del worker y los pasa a la UI via callback
"""
from app.core.app_state import AppState
from app.enums.e_camera_state import CameraState
from app.helpers.camera.camera_worker import CameraWorker
from app.models.ascii_params_model import AsciiParams
from typing import Callable


class CameraController:
    def __init__(self, on_frame: Callable, on_status: Callable | None = None):
        self._state     = AppState()
        self._worker: CameraWorker | None = None
        self._on_frame  = on_frame
        self._on_status = on_status or (lambda msg, lvl: None)

    def start(self, cam_index: int = 0) -> None:
        # Detener worker anterior y esperar que muera completamente
        # (join largo porque la apertura de cámara puede tardar hasta 9 s)
        if self._worker and self._worker.is_alive():
            self._worker.stop()
            self._worker.join(timeout=10.0)
            self._worker = None
        self._state.camera_state = CameraState.RUNNING
        self._worker = CameraWorker(
            cam_index=cam_index,
            params=self._state.params,
            on_frame=self._on_frame,
            on_status=self._on_status,
        )
        self._worker.start()

    def stop(self) -> None:
        if self._worker:
            self._worker.stop()
            self._worker.join(timeout=2.0)
            self._worker = None
        self._state.camera_state = CameraState.IDLE

    def pause(self) -> None:
        if self._worker:
            self._worker.pause()
        self._state.camera_state = CameraState.PAUSED

    def resume(self) -> None:
        if self._worker:
            self._worker.resume()
        self._state.camera_state = CameraState.RUNNING
