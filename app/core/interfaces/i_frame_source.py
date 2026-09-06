"""
i_frame_source.py — Protocolo estructural para fuentes de frames.

Define el contrato mínimo que cumple cualquier worker de captura, sea cual sea
su origen (webcam, pantalla de escritorio, un archivo de vídeo en el futuro…).
Al ser un Protocol (PEP 544) no exige herencia: basta con implementar los
métodos para satisfacerlo por duck-typing.

Implementaciones actuales:
    - CameraWorker  (app/helpers/camera/camera_worker.py)   → cv2.VideoCapture
    - ScreenWorker  (app/helpers/screen/screen_worker.py)   → mss (captura de pantalla)

Ambas derivan de BaseCaptureWorker (app/helpers/capture/base_capture_worker.py),
que centraliza la lógica común: threading, throttle de FPS, detección de lag,
reconexión y el pipeline ASCII (FramePreprocessor → AsciiConverter → AsciiRenderer).

Contrato de callbacks (recibidos en el constructor del worker):
    on_frame(AsciiFrame | None) — None indica error fatal e irrecuperable.
    on_status(msg: str, level: str) — mensajes info/warn/error para la UI.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class IFrameSource(Protocol):
    """Ciclo de vida común a toda fuente de frames ASCII."""

    def start(self) -> None:
        """Arranca la captura en su propio hilo (heredado de threading.Thread)."""
        ...

    def stop(self) -> None:
        """Solicita la parada e interrumpe cualquier apertura/reintento en curso."""
        ...

    def pause(self) -> None:
        """Suspende temporalmente la entrega de frames sin cerrar la fuente."""
        ...

    def resume(self) -> None:
        """Reanuda la captura tras un pause()."""
        ...

    def is_alive(self) -> bool:
        """True mientras el hilo del worker siga vivo."""
        ...
