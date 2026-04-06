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
