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
