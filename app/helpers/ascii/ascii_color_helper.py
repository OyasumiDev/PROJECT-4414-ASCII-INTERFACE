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
