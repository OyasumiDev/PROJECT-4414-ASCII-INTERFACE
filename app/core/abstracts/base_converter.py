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
