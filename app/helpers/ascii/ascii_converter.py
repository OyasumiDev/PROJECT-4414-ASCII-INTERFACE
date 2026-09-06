"""
ascii_converter.py  ← ALGORITMO PRINCIPAL
Mapea intensidad de píxel → carácter. Todo el mapeo es manual con numpy.

Dos entradas:
    to_index_grid(gray_small, invert, charset_key)
        Ruta rápida usada por el worker. Recibe la imagen en gris YA reducida a
        la rejilla (rows, cols) y devuelve el grid de ÍNDICES de carácter
        (numpy uint8) + la paleta. No construye ningún string.
    convert(frame, cols, invert, charset_key) -> str
        Compat: acepta un frame en gris a cualquier resolución y devuelve el
        arte ASCII como string multilínea (lo re-deriva a partir del grid).
"""
import cv2
import numpy as np

from app.enums.e_charset import CharSet

# Los caracteres de terminal son ~2× más altos que anchos: se compensa el
# aspect ratio con este factor al calcular el nº de filas.
_CHAR_ASPECT = 0.43


class AsciiConverter:
    def rows_for(self, cols: int, src_w: int, src_h: int) -> int:
        """Nº de filas ASCII que mantiene el aspect ratio de la fuente."""
        return max(1, int(cols * (src_h / max(1, src_w)) * _CHAR_ASPECT))

    def to_index_grid(
        self, gray_small: np.ndarray, invert: bool, charset_key: str
    ) -> tuple[np.ndarray, str]:
        """
        gray_small : imagen en gris uint8 YA redimensionada a (rows, cols).
        Devuelve   : (grid uint8 (rows, cols) con el índice en la paleta, chars).
        """
        chars = self._get_chars(charset_key, invert)
        n_max = len(chars) - 1
        grid = (gray_small.astype(np.float32) * (n_max / 255.0)).astype(np.uint8)
        np.clip(grid, 0, n_max, out=grid)          # defensivo (grid diminuto)
        return grid, chars

    def convert(self, frame: np.ndarray, cols: int, invert: bool, charset_key: str) -> str:
        """Compat: frame en gris (cualquier tamaño) → string ASCII multilínea."""
        h, w = frame.shape[:2]
        rows = self.rows_for(cols, w, h)
        small = cv2.resize(frame, (cols, rows), interpolation=cv2.INTER_AREA)
        grid, chars = self.to_index_grid(small, invert, charset_key)
        table = np.array(list(chars))
        return "\n".join("".join(row) for row in table[grid])

    def _get_chars(self, key: str, invert: bool) -> str:
        try:
            chars = CharSet[key].value
        except KeyError:
            chars = CharSet.SIMPLE.value
        if not chars:
            chars = CharSet.SIMPLE.value
        return chars[::-1] if invert else chars
