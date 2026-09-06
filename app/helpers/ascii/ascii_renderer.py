"""
ascii_renderer.py
Rasteriza la rejilla ASCII a un PNG base64.

RASTERIZADO POR ATLAS DE GLIFOS (vectorizado):
  - Cada carácter de la paleta se dibuja UNA vez a una celda char_w×char_h y se
    cachea en un atlas (n_chars, char_h, char_w). Cacheado por (font_size, chars).
  - Cada frame: máscara de tinta completa = atlas[grid] + reshape (una op numpy).
    No hay un draw.text() por carácter ni por línea.
  - Modo grises + colores por defecto → la máscara ES la imagen (modo "L").
  - Modo color → máscara × color real de cada celda (fusión SIMD con cv2.multiply).

ENTRADAS:
  render_grid_to_base64(grid, chars, params, color_cells=…)
      Ruta rápida del worker: recibe el grid de índices (numpy) y, en color, las
      celdas BGR ya a resolución de rejilla. Cero parsing de strings.
  render_to_base64(ascii_str, params, color_frame=…)
      Compat: reconstruye el grid desde el string y delega en la ruta rápida.

COSTE ACOTADO:
  El PNG se guarda con compress_level=1 (rápido) y el lienzo se limita a
  _MAX_OUT_W de ancho: por encima se hace UN cv2.resize(INTER_AREA). El detalle
  ASCII (nº de columnas) se conserva; sólo se recorta nitidez sub-glifo que el
  visor no llega a mostrar.
"""
import base64
import io

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.models.ascii_params_model import AsciiParams
from app.enums.e_charset import CharSet

_MAX_OUT_W = 1600   # ancho máximo del lienzo rasterizado


class AsciiRenderer:
    def __init__(self):
        self._font_cache: dict = {}
        self._atlas_cache: dict = {}   # (font_size, chars) -> (atlas, char_w, char_h)

    # ── API pública ─────────────────────────────────────────────────────────

    def render_grid_to_base64(
        self,
        grid: np.ndarray,
        chars: str,
        params: AsciiParams,
        color_cells: np.ndarray | None = None,
        bg_color: tuple = (0, 0, 0),
        fg_color: tuple = (255, 255, 255),
    ) -> str:
        """
        grid        : uint8 (n_rows, n_cols) con el índice de carácter por celda.
        chars       : paleta ya resuelta (misma que usó el converter).
        color_cells : BGR (n_rows, n_cols, 3) a resolución de rejilla, o None.
        """
        try:
            img = self._compose(grid, chars, params, color_cells, bg_color, fg_color)
        except Exception as e:
            print(f"[RENDER] ruta atlas falló ({type(e).__name__}: {e}); uso fallback")
            img = self._compose_fallback(grid, chars, params, color_cells, bg_color, fg_color)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=False, compress_level=1)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def render_to_base64(
        self,
        ascii_str: str,
        params: AsciiParams,
        color_frame: np.ndarray | None = None,
        bg_color: tuple = (0, 0, 0),
        fg_color: tuple = (255, 255, 255),
    ) -> str:
        """Compat: string ASCII → PNG base64 (reconstruye el grid y delega)."""
        chars = self._resolve_chars(params.charset, params.invert)
        lut, max_ord = self._char_lut(chars)

        lines = ascii_str.split("\n") or [""]
        n_rows = len(lines)
        n_cols = max((len(l) for l in lines), default=1) or 1
        if any(len(l) != n_cols for l in lines):
            lines = [l.ljust(n_cols, " ")[:n_cols] for l in lines]

        ords = np.frombuffer("".join(lines).encode("utf-32-le"), dtype=np.uint32)
        ords = np.where(ords <= max_ord, ords, 0)
        grid = lut[ords].reshape(n_rows, n_cols).astype(np.uint8)

        color_cells = None
        if params.color_mode and color_frame is not None:
            color_cells = cv2.resize(
                color_frame, (n_cols, n_rows), interpolation=cv2.INTER_AREA
            )
        return self.render_grid_to_base64(
            grid, chars, params, color_cells, bg_color, fg_color
        )

    # ── Composición (ruta rápida) ─────────────────────────────────────────

    def _compose(
        self,
        grid: np.ndarray,
        chars: str,
        params: AsciiParams,
        color_cells: np.ndarray | None,
        bg_color: tuple,
        fg_color: tuple,
    ) -> "Image.Image":
        n_rows, n_cols = grid.shape
        atlas, char_w, char_h = self._get_atlas(params.font_size, chars)

        # Máscara de tinta completa: (rows, cols, ch, cw) -> (rows*ch, cols*cw)
        tiles = atlas[grid]
        mask = np.ascontiguousarray(
            tiles.transpose(0, 2, 1, 3).reshape(n_rows * char_h, n_cols * char_w)
        )
        H, W = mask.shape

        if color_cells is not None:
            # Cada glifo toma el color real de su celda (fondo negro).
            rgb = cv2.cvtColor(color_cells, cv2.COLOR_BGR2RGB)
            color_layer = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_NEAREST)
            mask3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
            out = cv2.multiply(color_layer, mask3, scale=1.0 / 255.0)   # SIMD, uint8
            img = Image.fromarray(out, "RGB")
        elif tuple(fg_color) == (255, 255, 255) and tuple(bg_color) == (0, 0, 0):
            img = Image.fromarray(mask, "L")                            # la máscara ES la imagen
        else:
            m = mask[:, :, None].astype(np.uint16)
            fg = np.asarray(fg_color, np.uint16)
            bg = np.asarray(bg_color, np.uint16)
            out = ((m * fg + (255 - m) * bg) // 255).astype(np.uint8)
            img = Image.fromarray(out, "RGB")

        return self._cap_width(img)

    def _cap_width(self, img: "Image.Image") -> "Image.Image":
        if img.width <= _MAX_OUT_W:
            return img
        scale = _MAX_OUT_W / img.width
        arr = cv2.resize(
            np.asarray(img),
            (_MAX_OUT_W, max(1, round(img.height * scale))),
            interpolation=cv2.INTER_AREA,
        )
        return Image.fromarray(arr, img.mode)

    def _get_atlas(self, font_size: int, chars: str):
        """Rasteriza (y cachea) cada glifo de la paleta a una celda char_w×char_h."""
        key = (font_size, chars)
        cached = self._atlas_cache.get(key)
        if cached is not None:
            return cached

        font = self._get_font(font_size)
        char_w, char_h = self._get_char_size(font)
        atlas = np.zeros((len(chars), char_h, char_w), dtype=np.uint8)
        for i, ch in enumerate(chars):
            cell = Image.new("L", (char_w, char_h), 0)
            ImageDraw.Draw(cell).text((0, 0), ch, font=font, fill=255)
            atlas[i] = np.asarray(cell)

        result = (atlas, char_w, char_h)
        self._atlas_cache[key] = result
        return result

    # ── Fallback: bucle draw.text de siempre ─────────────────────────────

    def _compose_fallback(
        self, grid, chars, params, color_cells, bg_color, fg_color
    ) -> "Image.Image":
        font = self._get_font(params.font_size)
        char_w, char_h = self._get_char_size(font)
        table = np.array(list(chars))
        lines = ["".join(r) for r in table[grid]]
        n_rows, n_cols = grid.shape
        img = Image.new("RGB", (max(1, n_cols * char_w), max(1, n_rows * char_h)), bg_color)
        draw = ImageDraw.Draw(img)
        if color_cells is not None:
            rgb = cv2.cvtColor(color_cells, cv2.COLOR_BGR2RGB)
            for r, line in enumerate(lines):
                for c, ch in enumerate(line):
                    draw.text((c * char_w, r * char_h), ch, font=font,
                              fill=tuple(int(v) for v in rgb[r, c]))
        else:
            for r, line in enumerate(lines):
                draw.text((0, r * char_h), line, font=font, fill=fg_color)
        return self._cap_width(img)

    # ── Paleta / LUT (sólo para la ruta de compat con string) ────────────

    @staticmethod
    def _resolve_chars(key: str, invert: bool) -> str:
        """Idéntico a AsciiConverter._get_chars para que la paleta coincida."""
        try:
            chars = CharSet[key].value
        except KeyError:
            chars = CharSet.SIMPLE.value
        if not chars:
            chars = CharSet.SIMPLE.value
        return chars[::-1] if invert else chars

    @staticmethod
    def _char_lut(chars: str) -> tuple[np.ndarray, int]:
        max_ord = max(ord(c) for c in chars)
        lut = np.zeros(max_ord + 1, dtype=np.int64)
        for i, ch in enumerate(chars):
            lut[ord(ch)] = i
        return lut, max_ord

    # ── Fuente / métricas ────────────────────────────────────────────────

    def _get_font(self, size: int):
        if size not in self._font_cache:
            candidates = ["consolas.ttf", "cour.ttf", "lucon.ttf", "DejaVuSansMono.ttf"]
            loaded = None
            for name in candidates:
                try:
                    loaded = ImageFont.truetype(name, size)
                    break
                except Exception:
                    continue
            if loaded is None:
                try:
                    loaded = ImageFont.load_default(size=size)
                except TypeError:
                    loaded = ImageFont.load_default()
            self._font_cache[size] = loaded
        return self._font_cache[size]

    def _get_char_size(self, font) -> tuple[int, int]:
        try:
            try:
                w = max(1, round(font.getlength("A")))
            except AttributeError:
                bbox = font.getbbox("A")
                w = max(1, bbox[2] - bbox[0])
            try:
                ascent, descent = font.getmetrics()
                h = max(1, ascent + descent)
            except Exception:
                bbox = font.getbbox("Ay")
                h = max(1, bbox[3] - bbox[1])
            return w, h
        except Exception:
            return 6, 10
