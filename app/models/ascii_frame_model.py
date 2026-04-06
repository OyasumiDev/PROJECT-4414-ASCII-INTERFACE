from dataclasses import dataclass, field
import time


@dataclass
class AsciiFrame:
    """
    Resultado de un frame convertido a ASCII.
    ascii_str  → string listo para renderizar
    image_b64  → base64 PNG generado por ascii_renderer.py (para ft.Image)
    """
    ascii_str:  str   = ""
    image_b64:  str   = ""
    width:      int   = 0
    height:     int   = 0
    timestamp:  float = field(default_factory=time.time)
