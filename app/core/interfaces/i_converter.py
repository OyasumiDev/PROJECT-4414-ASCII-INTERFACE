"""
i_converter.py — Protocolo (interfaz) para conversores de frame a ASCII.

Define el contrato mínimo que debe cumplir cualquier clase que convierta
un frame numpy en un string de arte ASCII. Usar Protocol en lugar de ABC
permite duck-typing estructural: basta con que la clase implemente `convert`,
sin necesidad de heredar explícitamente.
"""

from typing import Protocol
import numpy as np


class IConverter(Protocol):
    """Interfaz estructural para conversores frame → ASCII."""

    def convert(self, frame: np.ndarray, cols: int, invert: bool, charset: str) -> str:
        """
        Convierte un frame en escala de grises a un string ASCII multilínea.

        Args:
            frame   : imagen numpy 2D (uint8, escala de grises).
            cols    : número de columnas de caracteres en el resultado.
            invert  : si True, invierte la paleta de caracteres.
            charset : clave del enum CharSet que define los caracteres a usar.

        Returns:
            String multilínea con el arte ASCII.
        """
        ...
