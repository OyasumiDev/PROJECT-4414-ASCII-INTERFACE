"""
ascii_renderer.py
Convierte el string ASCII a una PIL.Image y luego a base64 PNG.
Soporta dos modos:
  - Escala de grises (por defecto): un solo color de texto sobre fondo negro.
  - Color: cada carácter recibe el color real del píxel correspondiente en el frame.
"""
import base64
import io
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.models.ascii_params_model import AsciiParams


class AsciiRenderer:
    def __init__(self):
        self._font_cache: dict = {}

    def render_to_base64(
        self,
        ascii_str: str,
        params: AsciiParams,
        color_frame: np.ndarray | None = None,
        bg_color: tuple = (0, 0, 0),
        fg_color: tuple = (255, 255, 255),
    ) -> str:
        """
        Renderiza el string ASCII como imagen PNG en base64.

        Parámetros:
            color_frame → frame BGR original (solo se usa si params.color_mode=True)
            bg_color    → color de fondo
            fg_color    → color de texto en modo escala de grises
        """
        font           = self._get_font(params.font_size)
        char_w, char_h = self._get_char_size(font)

        lines  = ascii_str.split("\n")
        n_cols = max(len(l) for l in lines) if lines else 1
        n_rows = len(lines)

        img_w = max(1, n_cols * char_w)
        img_h = max(1, n_rows * char_h)

        img  = Image.new("RGB", (img_w, img_h), color=bg_color)
        draw = ImageDraw.Draw(img)

        if params.color_mode and color_frame is not None:
            # ── Modo color: samplear el píxel real para cada carácter ─────
            small_bgr = cv2.resize(color_frame, (n_cols, n_rows), interpolation=cv2.INTER_AREA)
            small_rgb = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)
            for row_idx, line in enumerate(lines):
                y = row_idx * char_h
                for col_idx, ch in enumerate(line):
                    r, g, b = small_rgb[row_idx, col_idx]
                    draw.text((col_idx * char_w, y), ch, font=font, fill=(int(r), int(g), int(b)))
        else:
            # ── Modo escala de grises (ruta rápida) ───────────────────────
            for row_idx, line in enumerate(lines):
                y = row_idx * char_h
                draw.text((0, y), line, font=font, fill=fg_color)

        # ── Convertir a base64 ────────────────────────────────────────────
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=False)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _get_font(self, size: int):
        if size not in self._font_cache:
            # Orden de candidatos monospace disponibles en Windows
            candidates = ["consolas.ttf", "cour.ttf", "lucon.ttf", "DejaVuSansMono.ttf"]
            loaded = None
            for name in candidates:
                try:
                    loaded = ImageFont.truetype(name, size)
                    break
                except Exception:
                    continue
            if loaded is None:
                # Pillow 10+ acepta size= en load_default
                try:
                    loaded = ImageFont.load_default(size=size)
                except TypeError:
                    loaded = ImageFont.load_default()
            self._font_cache[size] = loaded
        return self._font_cache[size]

    def _get_char_size(self, font) -> tuple[int, int]:
        try:
            # Ancho: advance width (incluye spacing) → más preciso para tiling
            try:
                w = max(1, round(font.getlength("A")))
            except AttributeError:
                bbox = font.getbbox("A")
                w = max(1, bbox[2] - bbox[0])
            # Alto: ascent+descent = altura real de línea (evita solapamiento/gaps)
            try:
                ascent, descent = font.getmetrics()
                h = max(1, ascent + descent)
            except Exception:
                bbox = font.getbbox("Ay")
                h = max(1, bbox[3] - bbox[1])
            return w, h
        except Exception:
            return 6, 10
