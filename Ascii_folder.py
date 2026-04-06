"""
setup_ascii_cam.py
Genera la estructura completa del proyecto ASCII Cam en la carpeta actual.
Uso: python setup_ascii_cam.py
"""

import os
import sys

# ── Colores para la terminal ──────────────────────────────────────────────────
GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

# ── Definición de carpetas ────────────────────────────────────────────────────
FOLDERS = [
    "assets/fonts",
    "assets/icons",
    "app/config",
    "app/core/abstracts",
    "app/core/interfaces",
    "app/core/patterns",
    "app/core/state",
    "app/models",
    "app/enums",
    "app/controllers",
    "app/helpers/ascii",
    "app/helpers/camera",
    "app/views/components/feedback",
]

# ── Contenido de cada archivo ─────────────────────────────────────────────────
FILES = {

    # ── Entry point ──────────────────────────────────────────────────────────
    "main.py": '''\
import flet as ft
from app.views.window_main import setup_window


def main(page: ft.Page):
    setup_window(page)


ft.app(target=main)
''',

    # ── Requirements ─────────────────────────────────────────────────────────
    "requirements.txt": '''\
flet>=0.21.0
opencv-python>=4.9.0
numpy>=1.26.0
Pillow>=10.3.0
python-dotenv>=1.0.0
''',

    # ── .env ─────────────────────────────────────────────────────────────────
    ".env": '''\
# Índice de cámara (0 = cámara por defecto)
CAM_INDEX=0

# Parámetros ASCII por defecto
DEFAULT_COLS=100
DEFAULT_FPS=15
DEFAULT_FONT_SIZE=8
DEFAULT_INVERT=false
DEFAULT_CHARSET=SIMPLE
''',

    # ── Config ───────────────────────────────────────────────────────────────
    "app/config/config.py": '''\
import os
from dotenv import load_dotenv

load_dotenv()

CAM_INDEX       = int(os.getenv("CAM_INDEX", 0))
DEFAULT_COLS    = int(os.getenv("DEFAULT_COLS", 100))
DEFAULT_FPS     = int(os.getenv("DEFAULT_FPS", 15))
DEFAULT_FONT_SIZE = int(os.getenv("DEFAULT_FONT_SIZE", 8))
DEFAULT_INVERT  = os.getenv("DEFAULT_INVERT", "false").lower() == "true"
DEFAULT_CHARSET = os.getenv("DEFAULT_CHARSET", "SIMPLE")

APP_TITLE = "ASCII Cam"
APP_WIDTH = 1200
APP_HEIGHT = 750
''',

    "app/config/settings.py": '''\
"""
Ajustes persistentes de la app (tema, última cámara usada, etc.)
"""

class AppSettings:
    theme: str = "dark"
    last_cam_index: int = 0
''',

    "app/config/__init__.py": "",

    # ── Core — abstracts ─────────────────────────────────────────────────────
    "app/core/abstracts/base_converter.py": '''\
from abc import ABC, abstractmethod
import numpy as np


class BaseConverter(ABC):
    """
    Contrato base para cualquier conversor de frame → ASCII.
    Implementa convert() en tu subclase.
    """

    @abstractmethod
    def convert(self, frame: np.ndarray, cols: int, invert: bool, charset: str) -> str:
        """
        Recibe un frame en escala de grises (numpy 2D) y devuelve
        el string ASCII correspondiente.
        """
        ...
''',

    "app/core/abstracts/__init__.py": "",

    # ── Core — interfaces ────────────────────────────────────────────────────
    "app/core/interfaces/i_converter.py": '''\
from typing import Protocol
import numpy as np


class IConverter(Protocol):
    def convert(self, frame: np.ndarray, cols: int, invert: bool, charset: str) -> str:
        ...
''',

    "app/core/interfaces/i_observer.py": '''\
from typing import Protocol, Any


class IObserver(Protocol):
    def update(self, data: Any) -> None:
        ...


class IObservable(Protocol):
    def subscribe(self, observer: IObserver) -> None:
        ...

    def notify(self, data: Any) -> None:
        ...
''',

    "app/core/interfaces/__init__.py": "",

    # ── Core — patterns ──────────────────────────────────────────────────────
    "app/core/patterns/singleton.py": '''\
class SingletonMeta(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
''',

    "app/core/patterns/observable.py": '''\
from app.core.interfaces.i_observer import IObserver
from typing import Any


class Observable:
    def __init__(self):
        self._observers: list[IObserver] = []

    def subscribe(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, data: Any) -> None:
        for observer in self._observers:
            observer.update(data)
''',

    "app/core/patterns/__init__.py": "",

    # ── Core — state ─────────────────────────────────────────────────────────
    "app/core/state/camera_state.py": '''\
from app.enums.e_camera_state import CameraState


class CameraStateManager:
    def __init__(self):
        self._state = CameraState.IDLE

    @property
    def state(self) -> CameraState:
        return self._state

    def set(self, state: CameraState) -> None:
        self._state = state

    def is_running(self) -> bool:
        return self._state == CameraState.RUNNING
''',

    "app/core/state/__init__.py": "",

    # ── Core — app_state ─────────────────────────────────────────────────────
    "app/core/app_state.py": '''\
from app.core.patterns.singleton import SingletonMeta
from app.models.ascii_params_model import AsciiParams
from app.enums.e_camera_state import CameraState


class AppState(metaclass=SingletonMeta):
    def __init__(self):
        self.params: AsciiParams = AsciiParams()
        self.camera_state: CameraState = CameraState.IDLE
        self.current_cam_index: int = 0
''',

    "app/core/__init__.py": "",

    # ── Models ───────────────────────────────────────────────────────────────
    "app/models/ascii_params_model.py": '''\
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
    cols: int       = DEFAULT_COLS
    fps: int        = DEFAULT_FPS
    font_size: int  = DEFAULT_FONT_SIZE
    invert: bool    = DEFAULT_INVERT
    charset: str    = DEFAULT_CHARSET   # key del enum CharSet
    color_mode: bool = False            # True = modo color RGB
''',

    "app/models/ascii_frame_model.py": '''\
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
''',

    "app/models/__init__.py": "",

    # ── Enums ────────────────────────────────────────────────────────────────
    "app/enums/e_charset.py": '''\
from enum import Enum


class CharSet(Enum):
    """
    Conjuntos de caracteres disponibles para la conversión ASCII.
    El orden va de más oscuro a más claro (intensidad 0→255).
    """
    SIMPLE  = " .:-=+*#%@"
    BLOCKS  = " ░▒▓█"
    DENSE   = " .\':;Il!i><~+_-?][}{)(|\\/*^CJUYXzo0OQ@#MW&8B%$"
    BRAILLE = " ⠁⠃⠇⠏⠟⠿⣿"
    CUSTOM  = ""   # el usuario define su propio string en UI
''',

    "app/enums/e_camera_state.py": '''\
from enum import Enum


class CameraState(Enum):
    IDLE    = "idle"
    RUNNING = "running"
    PAUSED  = "paused"
    ERROR   = "error"
''',

    "app/enums/__init__.py": "",

    # ── Controllers ──────────────────────────────────────────────────────────
    "app/controllers/camera_controller.py": '''\
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
    def __init__(self, on_frame: Callable):
        self._state  = AppState()
        self._worker: CameraWorker | None = None
        self._on_frame = on_frame  # callback → ascii_display.py

    def start(self, cam_index: int = 0) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._state.camera_state = CameraState.RUNNING
        self._worker = CameraWorker(
            cam_index=cam_index,
            params=self._state.params,
            on_frame=self._on_frame,
        )
        self._worker.start()

    def stop(self) -> None:
        if self._worker:
            self._worker.stop()
            self._worker.join()
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
''',

    "app/controllers/params_controller.py": '''\
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
        self._state.params.fps = max(1, min(60, value))

    def set_font_size(self, value: int) -> None:
        self._state.params.font_size = max(4, min(24, value))

    def set_invert(self, value: bool) -> None:
        self._state.params.invert = value

    def set_charset(self, key: str) -> None:
        self._state.params.charset = key

    def set_color_mode(self, value: bool) -> None:
        self._state.params.color_mode = value
''',

    "app/controllers/__init__.py": "",

    # ── Helpers — ascii ──────────────────────────────────────────────────────
    "app/helpers/ascii/ascii_converter.py": '''\
"""
ascii_converter.py  ← TU ALGORITMO PRINCIPAL
Convierte un frame numpy (escala de grises) a un string ASCII.
No usa ninguna librería que haga la conversión automáticamente.
Todo el mapeo pixel → char es manual con numpy.
"""
import numpy as np
from app.enums.e_charset import CharSet


class AsciiConverter:
    def convert(self, frame: np.ndarray, cols: int, invert: bool, charset_key: str) -> str:
        """
        Parámetros:
            frame       → numpy 2D (escala de grises, valores 0-255)
            cols        → número de columnas de caracteres en el output
            invert      → invertir la paleta (útil con fondo blanco)
            charset_key → key de CharSet enum

        Retorna:
            string multilínea con el arte ASCII
        """
        chars = self._get_chars(charset_key, invert)

        # ── 1. Obtener dimensiones originales del frame ──────────────────
        h_orig, w_orig = frame.shape

        # ── 2. Calcular filas manteniendo aspect ratio ───────────────────
        #       Los chars son más altos que anchos (~2:1), se compensa con 0.43
        char_aspect = 0.43
        rows = max(1, int(cols * (h_orig / w_orig) * char_aspect))

        # ── 3. Redimensionar frame al tamaño de la cuadrícula ASCII ──────
        import cv2
        small = cv2.resize(frame, (cols, rows), interpolation=cv2.INTER_AREA)

        # ── 4. Mapear cada pixel a un carácter ───────────────────────────
        #       Normalizar 0-255 → índice en chars
        n_chars   = len(chars) - 1
        char_grid = (small / 255.0 * n_chars).astype(int)

        # ── 5. Construir string fila por fila ────────────────────────────
        lines = ["".join(chars[char_grid[y, x]] for x in range(cols)) for y in range(rows)]

        return "\n".join(lines)

    def _get_chars(self, key: str, invert: bool) -> str:
        try:
            chars = CharSet[key].value
        except KeyError:
            chars = CharSet.SIMPLE.value
        if not chars:
            chars = CharSet.SIMPLE.value
        return chars[::-1] if invert else chars
''',

    "app/helpers/ascii/ascii_renderer.py": '''\
"""
ascii_renderer.py
Convierte el string ASCII a una PIL.Image y luego a base64 PNG.
Flet consume el base64 en ft.Image(src_base64=...).
"""
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from app.models.ascii_params_model import AsciiParams


class AsciiRenderer:
    def __init__(self):
        self._font_cache: dict = {}

    def render_to_base64(
        self,
        ascii_str: str,
        params: AsciiParams,
        bg_color: tuple = (10, 10, 10),
        fg_color: tuple = (0, 255, 70),
    ) -> str:
        """
        Renderiza el string ASCII como imagen PNG en base64.

        Puedes cambiar bg_color/fg_color para distintos temas:
            Verde terminal clásico : bg=(10,10,10)   fg=(0,255,70)
            Blanco sobre negro     : bg=(0,0,0)       fg=(255,255,255)
            Ámbar retro            : bg=(20,10,0)      fg=(255,176,0)
        """
        font      = self._get_font(params.font_size)
        char_w, char_h = self._get_char_size(font)

        lines  = ascii_str.split("\n")
        n_cols = max(len(l) for l in lines) if lines else 1
        n_rows = len(lines)

        img_w = n_cols * char_w
        img_h = n_rows * char_h

        img  = Image.new("RGB", (img_w, img_h), color=bg_color)
        draw = ImageDraw.Draw(img)

        for row_idx, line in enumerate(lines):
            y = row_idx * char_h
            draw.text((0, y), line, font=font, fill=fg_color)

        # ── Convertir a base64 ────────────────────────────────────────────
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=False)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        if size not in self._font_cache:
            try:
                # Intenta cargar fuente monospace del sistema
                self._font_cache[size] = ImageFont.truetype("consola.ttf", size)
            except Exception:
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def _get_char_size(self, font) -> tuple[int, int]:
        try:
            bbox = font.getbbox("A")
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            return 6, 10
''',

    "app/helpers/ascii/ascii_color_helper.py": '''\
"""
ascii_color_helper.py
Extrae el color promedio de cada bloque de píxeles del frame original (BGR).
Usado en modo color para colorear cada carácter individualmente.
"""
import numpy as np
import cv2


class AsciiColorHelper:
    def extract_block_colors(
        self,
        frame_bgr: np.ndarray,
        cols: int,
        rows: int,
    ) -> list[list[tuple[int, int, int]]]:
        """
        Retorna una grilla [rows][cols] de colores RGB promedio por bloque.
        """
        h, w = frame_bgr.shape[:2]
        cell_w = w // cols
        cell_h = h // rows

        color_grid = []
        for r in range(rows):
            row_colors = []
            for c in range(cols):
                y1, y2 = r * cell_h, (r + 1) * cell_h
                x1, x2 = c * cell_w, (c + 1) * cell_w
                block = frame_bgr[y1:y2, x1:x2]
                avg_bgr = block.mean(axis=(0, 1)).astype(int)
                # Convertir BGR → RGB
                row_colors.append((int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0])))
            color_grid.append(row_colors)
        return color_grid
''',

    "app/helpers/ascii/__init__.py": "",

    # ── Helpers — camera ─────────────────────────────────────────────────────
    "app/helpers/camera/camera_worker.py": '''\
"""
camera_worker.py
Thread que captura frames de la webcam en loop,
los preprocesa y llama on_frame() con el AsciiFrame resultante.
"""
import threading
import time
import cv2
import numpy as np

from app.models.ascii_params_model import AsciiParams
from app.models.ascii_frame_model import AsciiFrame
from app.helpers.camera.frame_preprocessor import FramePreprocessor
from app.helpers.ascii.ascii_converter import AsciiConverter
from app.helpers.ascii.ascii_renderer import AsciiRenderer
from typing import Callable


class CameraWorker(threading.Thread):
    def __init__(self, cam_index: int, params: AsciiParams, on_frame: Callable):
        super().__init__(daemon=True)
        self._cam_index  = cam_index
        self._params     = params
        self._on_frame   = on_frame
        self._running    = False
        self._paused     = False
        self._lock       = threading.Lock()

        self._preprocessor = FramePreprocessor()
        self._converter    = AsciiConverter()
        self._renderer     = AsciiRenderer()

    def run(self) -> None:
        cap = cv2.VideoCapture(self._cam_index)
        if not cap.isOpened():
            self._on_frame(None)  # señal de error
            return

        self._running = True
        while self._running:
            if self._paused:
                time.sleep(0.05)
                continue

            ret, frame_bgr = cap.read()
            if not ret:
                break

            with self._lock:
                params = self._params  # referencia — se actualiza en tiempo real

            # ── Preprocesar ───────────────────────────────────────────────
            gray = self._preprocessor.to_gray(frame_bgr)

            # ── Convertir a ASCII ─────────────────────────────────────────
            ascii_str = self._converter.convert(
                frame   = gray,
                cols    = params.cols,
                invert  = params.invert,
                charset_key = params.charset,
            )

            # ── Renderizar a imagen base64 ────────────────────────────────
            image_b64 = self._renderer.render_to_base64(ascii_str, params)

            # ── Emitir frame ──────────────────────────────────────────────
            ascii_frame = AsciiFrame(
                ascii_str = ascii_str,
                image_b64 = image_b64,
            )
            self._on_frame(ascii_frame)

            # ── Respetar FPS target ───────────────────────────────────────
            time.sleep(1.0 / max(1, params.fps))

        cap.release()

    def stop(self) -> None:
        self._running = False

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False
''',

    "app/helpers/camera/frame_preprocessor.py": '''\
"""
frame_preprocessor.py
Operaciones de preprocesamiento del frame antes de la conversión ASCII.
Todo con numpy + cv2, sin librerías de alto nivel.
"""
import cv2
import numpy as np


class FramePreprocessor:
    def to_gray(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Convierte BGR a escala de grises."""
        return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    def normalize(self, frame: np.ndarray) -> np.ndarray:
        """Normaliza el contraste del frame (CLAHE)."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(frame)

    def flip_horizontal(self, frame: np.ndarray) -> np.ndarray:
        """Voltea el frame horizontalmente (modo espejo)."""
        return cv2.flip(frame, 1)
''',

    "app/helpers/camera/__init__.py": "",
    "app/helpers/__init__.py": "",
    "app/helpers/ui_factory.py": '''\
"""
ui_factory.py
Factory de controles Flet reutilizables para la app.
"""
import flet as ft


class UIFactory:
    @staticmethod
    def slider(
        label: str,
        min_val: float,
        max_val: float,
        value: float,
        on_change,
        divisions: int = 100,
    ) -> ft.Column:
        lbl = ft.Text(label, size=12, color=ft.Colors.WHITE70)
        val_text = ft.Text(str(int(value)), size=12, width=40, text_align=ft.TextAlign.RIGHT)

        def _change(e):
            val_text.value = str(int(e.control.value))
            val_text.update()
            on_change(e.control.value)

        slider = ft.Slider(
            min=min_val, max=max_val, value=value,
            divisions=divisions, on_change=_change,
            active_color=ft.Colors.GREEN_400,
        )
        return ft.Column([
            ft.Row([lbl, val_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            slider,
        ], spacing=0)

    @staticmethod
    def icon_button(icon, tooltip: str, on_click) -> ft.IconButton:
        return ft.IconButton(
            icon=icon, tooltip=tooltip, on_click=on_click,
            icon_color=ft.Colors.WHITE70,
        )
''',

    "app/helpers/validators.py": '''\
def validate_cam_index(value) -> int:
    try:
        v = int(value)
        return max(0, min(v, 10))
    except (ValueError, TypeError):
        return 0


def validate_cols(value) -> int:
    try:
        return max(20, min(int(value), 300))
    except (ValueError, TypeError):
        return 100
''',

    # ── Views ────────────────────────────────────────────────────────────────
    "app/views/window_main.py": '''\
import flet as ft
from app.config.config import APP_TITLE, APP_WIDTH, APP_HEIGHT
from app.views.ascii_cam_view import AsciiCamView


def setup_window(page: ft.Page) -> None:
    page.title            = APP_TITLE
    page.theme_mode       = ft.ThemeMode.DARK
    page.bgcolor          = ft.Colors.BLACK
    page.window.width     = APP_WIDTH
    page.window.height    = APP_HEIGHT
    page.window.resizable = True
    page.padding          = 0

    view = AsciiCamView(page)
    page.add(view.build())
    page.update()
''',

    "app/views/ascii_cam_view.py": '''\
"""
ascii_cam_view.py
Vista principal — orquesta los componentes de la UI.
No contiene lógica de negocio: llama a controllers.
"""
import flet as ft
from app.controllers.camera_controller import CameraController
from app.controllers.params_controller import ParamsController
from app.views.components.ascii_display import AsciiDisplay
from app.views.components.params_panel import ParamsPanel
from app.views.components.camera_controls import CameraControls
from app.models.ascii_frame_model import AsciiFrame


class AsciiCamView:
    def __init__(self, page: ft.Page):
        self._page   = page
        self._params = ParamsController()
        self._display = AsciiDisplay()
        self._camera  = CameraController(on_frame=self._on_frame)

    def _on_frame(self, frame: AsciiFrame | None) -> None:
        """Callback que llega desde CameraWorker (hilo background)."""
        if frame is None:
            return
        self._display.update(frame.image_b64, self._page)

    def build(self) -> ft.Row:
        controls = CameraControls(
            on_start  = lambda _: self._camera.start(),
            on_stop   = lambda _: self._camera.stop(),
            on_pause  = lambda _: self._camera.pause(),
            on_resume = lambda _: self._camera.resume(),
        )
        panel = ParamsPanel(self._params)

        sidebar = ft.Container(
            content=ft.Column([
                controls.build(),
                ft.Divider(color=ft.Colors.WHITE12),
                panel.build(),
            ], spacing=12, scroll=ft.ScrollMode.AUTO),
            width=280,
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.GREY_900),
            padding=16,
        )

        return ft.Row([
            self._display.build(),
            sidebar,
        ], spacing=0, expand=True)
''',

    "app/views/__init__.py": "",

    # ── Components ───────────────────────────────────────────────────────────
    "app/views/components/ascii_display.py": '''\
"""
ascii_display.py
Muestra el frame ASCII como ft.Image(src_base64=...).
La actualización se hace desde el hilo de cámara vía page.update().
"""
import flet as ft


class AsciiDisplay:
    def __init__(self):
        self._image = ft.Image(
            src_base64="",
            fit=ft.ImageFit.CONTAIN,
            expand=True,
        )

    def build(self) -> ft.Container:
        return ft.Container(
            content=self._image,
            expand=True,
            bgcolor=ft.Colors.BLACK,
        )

    def update(self, image_b64: str, page: ft.Page) -> None:
        """Llamado desde el hilo background — actualiza la imagen."""
        self._image.src_base64 = image_b64
        try:
            page.update()
        except Exception:
            pass  # conexión cerrada al salir
''',

    "app/views/components/params_panel.py": '''\
"""
params_panel.py
Panel lateral con sliders y dropdowns para ajustar parámetros en tiempo real.
"""
import flet as ft
from app.controllers.params_controller import ParamsController
from app.helpers.ui_factory import UIFactory
from app.enums.e_charset import CharSet


class ParamsPanel:
    def __init__(self, controller: ParamsController):
        self._ctrl = controller

    def build(self) -> ft.Column:
        params = self._ctrl.params

        charset_dropdown = ft.Dropdown(
            label="Charset",
            value=params.charset,
            options=[ft.dropdown.Option(k.name) for k in CharSet if k.value],
            on_change=lambda e: self._ctrl.set_charset(e.control.value),
            bgcolor=ft.Colors.GREY_900,
            color=ft.Colors.WHITE,
        )

        invert_switch = ft.Switch(
            label="Invertir",
            value=params.invert,
            on_change=lambda e: self._ctrl.set_invert(e.control.value),
            active_color=ft.Colors.GREEN_400,
        )

        color_switch = ft.Switch(
            label="Modo color",
            value=params.color_mode,
            on_change=lambda e: self._ctrl.set_color_mode(e.control.value),
            active_color=ft.Colors.GREEN_400,
        )

        return ft.Column([
            ft.Text("Parámetros", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            UIFactory.slider("Columnas",   20,  300, params.cols,      self._ctrl.set_cols,      divisions=280),
            UIFactory.slider("FPS target",  1,   60, params.fps,       self._ctrl.set_fps,       divisions=59),
            UIFactory.slider("Tamaño fuente", 4, 24, params.font_size, self._ctrl.set_font_size, divisions=20),
            charset_dropdown,
            invert_switch,
            color_switch,
        ], spacing=12)
''',

    "app/views/components/camera_controls.py": '''\
"""
camera_controls.py
Botones de control de cámara: start / stop / pause / resume + selector de índice.
"""
import flet as ft
from typing import Callable


class CameraControls:
    def __init__(
        self,
        on_start:  Callable,
        on_stop:   Callable,
        on_pause:  Callable,
        on_resume: Callable,
    ):
        self._on_start  = on_start
        self._on_stop   = on_stop
        self._on_pause  = on_pause
        self._on_resume = on_resume

    def build(self) -> ft.Column:
        cam_index = ft.TextField(
            label="Índice cámara",
            value="0",
            width=100,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREY_900,
            border_color=ft.Colors.WHITE24,
        )

        return ft.Column([
            ft.Text("Controles", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            cam_index,
            ft.Row([
                ft.ElevatedButton(
                    "Start", icon=ft.Icons.PLAY_ARROW,
                    on_click=self._on_start,
                    bgcolor=ft.Colors.GREEN_800,
                    color=ft.Colors.WHITE,
                ),
                ft.ElevatedButton(
                    "Stop", icon=ft.Icons.STOP,
                    on_click=self._on_stop,
                    bgcolor=ft.Colors.RED_900,
                    color=ft.Colors.WHITE,
                ),
            ], spacing=8),
            ft.Row([
                ft.OutlinedButton("Pause",  on_click=self._on_pause),
                ft.OutlinedButton("Resume", on_click=self._on_resume),
            ], spacing=8),
        ], spacing=10)
''',

    "app/views/components/theme_switcher.py": '''\
import flet as ft


class ThemeSwitcher:
    def build(self, page: ft.Page) -> ft.IconButton:
        def toggle(e):
            page.theme_mode = (
                ft.ThemeMode.LIGHT
                if page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            page.update()

        return ft.IconButton(
            icon=ft.Icons.BRIGHTNESS_6,
            tooltip="Cambiar tema",
            on_click=toggle,
            icon_color=ft.Colors.WHITE70,
        )
''',

    "app/views/components/__init__.py": "",

    # ── Feedback ─────────────────────────────────────────────────────────────
    "app/views/components/feedback/snackbar.py": '''\
import flet as ft


def show_snackbar(page: ft.Page, message: str, color: str = ft.Colors.GREEN_700) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=color,
        open=True,
    )
    page.update()
''',

    "app/views/components/feedback/alert_banner.py": '''\
import flet as ft


def show_error(page: ft.Page, message: str) -> None:
    banner = ft.Banner(
        bgcolor=ft.Colors.RED_900,
        leading=ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE),
        content=ft.Text(message, color=ft.Colors.WHITE),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda _: close(page)),
        ],
        open=True,
    )
    page.banner = banner
    page.update()


def close(page: ft.Page) -> None:
    page.banner.open = False
    page.update()
''',

    "app/views/components/feedback/__init__.py": "",
}


# ── Función principal ─────────────────────────────────────────────────────────
def setup():
    base = os.getcwd()
    project_name = os.path.basename(base)

    log(f"\n{BOLD}ASCII Cam — generando estructura en:{RESET}", CYAN)
    log(f"  {base}\n", YELLOW)

    # Crear carpetas
    for folder in FOLDERS:
        path = os.path.join(base, folder)
        os.makedirs(path, exist_ok=True)
        log(f"  {GREEN}[+]{RESET} {folder}/")

    print()

    # Crear archivos
    created = 0
    skipped = 0
    for rel_path, content in FILES.items():
        abs_path = os.path.join(base, rel_path)
        if os.path.exists(abs_path):
            log(f"  {YELLOW}[~]{RESET} {rel_path}  (ya existe, no sobreescrito)")
            skipped += 1
            continue
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        log(f"  {GREEN}[+]{RESET} {rel_path}")
        created += 1

    print()
    log(f"{BOLD}Listo.{RESET}  {GREEN}{created} archivos creados{RESET}"
        + (f", {YELLOW}{skipped} omitidos{RESET}" if skipped else "") + ".")
    log(f"\nSiguientes pasos:", BOLD)
    log(f"  1.  pip install -r requirements.txt")
    log(f"  2.  python main.py")
    log(f"\nEl proyecto '{project_name}' está listo para desarrollar.\n", CYAN)


if __name__ == "__main__":
    setup()
