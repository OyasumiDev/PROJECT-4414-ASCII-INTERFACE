from dataclasses import dataclass, field
from app.config.config import (
    DEFAULT_COLS, DEFAULT_FPS, DEFAULT_FONT_SIZE,
    DEFAULT_INVERT, DEFAULT_CHARSET
)


@dataclass
class AsciiParams:
    """
    Todos los parámetros configurables de la conversión ASCII.
    Modifica estos valores desde params_controller.py.
    """
    cols: int        = DEFAULT_COLS
    fps: int         = DEFAULT_FPS
    font_size: int   = DEFAULT_FONT_SIZE
    invert: bool     = DEFAULT_INVERT
    charset: str     = DEFAULT_CHARSET   # key del enum CharSet
    color_mode: bool = False             # True = modo color RGB
    resolution: tuple = (640, 480)       # (width, height): 480p / 720p / 1080p
