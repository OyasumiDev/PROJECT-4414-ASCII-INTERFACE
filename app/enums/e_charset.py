from enum import Enum


class CharSet(Enum):
    """
    Conjuntos de caracteres disponibles para la conversión ASCII.
    El orden va de más oscuro a más claro (intensidad 0→255).
    """
    SIMPLE  = " .:-=+*#%@"
    BLOCKS  = " ░▒▓█"
    DENSE   = " .':;Il!i><~+_-?][}{)(|\/*^CJUYXzo0OQ@#MW&8B%$"
    BRAILLE = " ⠁⠃⠇⠏⠟⠿⣿"
    CUSTOM  = ""   # el usuario define su propio string en UI
