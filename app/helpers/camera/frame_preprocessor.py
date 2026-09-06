"""
frame_preprocessor.py
Operaciones de preprocesamiento del frame antes de la conversión ASCII.
Todo con numpy + cv2, sin librerías de alto nivel.

Optimización: el objeto CLAHE se crea UNA vez (antes se instanciaba en cada
frame) y el brillo se aplica con una LUT gamma cacheada (cv2.LUT es SIMD).
En el pipeline nuevo estas operaciones corren sobre la imagen ya reducida a
la rejilla ASCII (cols×rows), así que su coste es prácticamente nulo.
"""
import cv2
import numpy as np


class FramePreprocessor:
    def __init__(self):
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self._bright_lut: dict[int, np.ndarray] = {}

    def to_gray(self, frame_bgr: np.ndarray) -> np.ndarray:
        """Convierte BGR a escala de grises."""
        return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

    def normalize(self, frame: np.ndarray) -> np.ndarray:
        """Normaliza el contraste local del frame (CLAHE, objeto reutilizado)."""
        return self._clahe.apply(frame)

    def apply_brightness(self, frame: np.ndarray, brightness: int) -> np.ndarray:
        """
        Ajusta el brillo con una curva gamma.

        brightness = 100 → sin cambios (se devuelve el frame tal cual).
        brightness > 100 → aclara (sube medios/sombras sin quemar altas luces).
        brightness < 100 → oscurece.

        La LUT (256 entradas uint8) se calcula una vez por valor y se cachea;
        cv2.LUT la aplica a los 3 canales de golpe.
        """
        b = int(brightness)
        if b == 100:
            return frame
        lut = self._bright_lut.get(b)
        if lut is None:
            gamma = 100.0 / max(1, b)                       # <1 aclara, >1 oscurece
            x = np.arange(256, dtype=np.float32) / 255.0
            lut = np.clip(np.power(x, gamma) * 255.0, 0, 255).astype(np.uint8)
            self._bright_lut[b] = lut
        return cv2.LUT(frame, lut)

    def flip_horizontal(self, frame: np.ndarray) -> np.ndarray:
        """Voltea el frame horizontalmente (modo espejo)."""
        return cv2.flip(frame, 1)
