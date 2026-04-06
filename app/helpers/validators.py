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
    Normaliza el número de columnas ASCII al rango [20, 300].

    Menos de 20 columnas produce arte ilegible; más de 300 puede saturar
    el renderizador con imágenes muy grandes en modo color.

    Args:
        value: cualquier valor; se intenta convertir a int.

    Returns:
        Entero entre 20 y 300 inclusive. Devuelve 100 (default) si falla.
    """
    try:
        return max(20, min(int(value), 300))
    except (ValueError, TypeError):
        return 100
