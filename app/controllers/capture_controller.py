"""
capture_controller.py — Orquesta el ciclo de vida de la fuente de captura activa.

Generaliza el antiguo CameraController: según el SourceType del CaptureRequest
instancia el worker adecuado (CameraWorker o ScreenWorker). Ambos derivan de
BaseCaptureWorker, por lo que comparten exactamente el mismo ciclo de vida
start / stop / pause / resume y el mismo contrato de callbacks.

Antes de arrancar un worker nuevo detiene el anterior y hace join con timeout
(10 s: la apertura de cámara puede tardar varios segundos entre backends).

AppState guarda la fuente activa y sus parámetros específicos para que el resto
de la app pueda consultarlos.

Nota: app/controllers/camera_controller.py se mantiene como estaba por
compatibilidad; la app usa este CaptureController.
"""
from typing import Callable

from app.core.app_state import AppState
from app.enums.e_camera_state import CameraState
from app.enums.e_source_type import SourceType
from app.helpers.capture.base_capture_worker import BaseCaptureWorker
from app.helpers.camera.camera_worker import CameraWorker
from app.helpers.screen.screen_worker import ScreenWorker
from app.models.capture_request_model import CaptureRequest


class CaptureController:
    """Punto único de control de la captura, sea cámara o pantalla."""

    def __init__(self, on_frame: Callable, on_status: Callable | None = None):
        self._state     = AppState()
        self._worker: BaseCaptureWorker | None = None
        self._on_frame  = on_frame
        self._on_status = on_status or (lambda msg, lvl: None)

    def start(self, request: CaptureRequest) -> None:
        # Detener worker anterior y esperar a que muera del todo.
        if self._worker and self._worker.is_alive():
            self._worker.stop()
            self._worker.join(timeout=10.0)
        self._worker = None

        self._state.source_type = request.source_type

        if request.source_type == SourceType.SCREEN:
            self._state.current_monitor_index = request.monitor_index
            self._state.screen_region         = request.region
            self._state.screen_quality        = request.quality
            worker: BaseCaptureWorker = ScreenWorker(
                params=self._state.params,
                on_frame=self._on_frame,
                on_status=self._on_status,
                monitor_index=request.monitor_index,
                region=request.region,
                quality=request.quality,
            )
        else:
            self._state.current_cam_index = request.cam_index
            worker = CameraWorker(
                cam_index=request.cam_index,
                params=self._state.params,
                on_frame=self._on_frame,
                on_status=self._on_status,
            )

        self._state.camera_state = CameraState.RUNNING
        self._worker = worker
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
