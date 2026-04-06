"""
params_controller.py
Aplica cambios de parámetros en tiempo real sin reiniciar la cámara.
La UI llama a estos métodos directamente desde params_panel.py.
"""
from app.core.app_state import AppState
from app.models.ascii_params_model import AsciiParams


class ParamsController:
    def __init__(self):
        self._state = AppState()

    @property
    def params(self) -> AsciiParams:
        return self._state.params

    def set_cols(self, value: int) -> None:
        self._state.params.cols = max(20, min(300, value))

    def set_fps(self, value: int) -> None:
        self._state.params.fps = max(1, min(120, value))

    def set_resolution(self, width: int, height: int) -> None:
        self._state.params.resolution = (width, height)

    def set_font_size(self, value: int) -> None:
        self._state.params.font_size = max(4, min(24, value))

    def set_invert(self, value: bool) -> None:
        self._state.params.invert = value

    def set_charset(self, key: str) -> None:
        self._state.params.charset = key

    def set_color_mode(self, value: bool) -> None:
        self._state.params.color_mode = value
