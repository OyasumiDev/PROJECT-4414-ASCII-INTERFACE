"""
validators.py — Funciones de validación y normalización de entradas.

Garantizan que los valores provenientes de la UI o del archivo .env estén
dentro de rangos seguros antes de llegar a los modelos o al worker.
No lanzan excepciones: ante cualquier valor inválido devuelven un default.
"""


def validate_cam_index(value) -> int:
    """
    Normaliza el índice de cámara al rango [0, 10].

    Args:
        value: cualquier valor; se intenta convertir a int.

    Returns:
        Entero entre 0 y 10 inclusive. Devuelve 0 si la conversión falla.
    """
    try:
        v = int(value)
        return max(0, min(v, 10))
    except (ValueError, TypeError):
        return 0


def validate_cols(value) -> int:
    """
    Normaliza el número de columnas ASCII al rango [20, 500].

    Menos de 20 columnas produce arte ilegible; el tope de 500 permite que la
    captura de pantalla sea legible sin generar imágenes desmesuradas.

    Args:
        value: cualquier valor; se intenta convertir a int.

    Returns:
        Entero entre 20 y 500 inclusive. Devuelve 100 (default) si falla.
    """
    try:
        return max(20, min(int(value), 500))
    except (ValueError, TypeError):
        return 100
