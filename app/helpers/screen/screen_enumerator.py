"""
screen_enumerator.py — Lista los monitores disponibles para captura, vía mss.

`mss.mss().monitors` devuelve:
    índice 0 → rectángulo que engloba TODOS los monitores (escritorio virtual).
    índice 1..N → cada monitor físico, en el orden que reporta el sistema.

list_monitors() normaliza eso a una lista [(mss_index, etiqueta)] lista para
poblar un QComboBox. La opción "Todos los monitores" sólo se ofrece cuando hay
2 o más monitores físicos (con uno solo sería redundante).
"""


def list_monitors() -> list[tuple[int, str]]:
    """
    Returns list of (mss_monitor_index, display_name).

    Nunca lanza: ante cualquier fallo (mss no instalado, backend sin display)
    devuelve un único monitor principal ficticio con índice 1.
    """
    try:
        import mss

        factory = getattr(mss, "MSS", None) or getattr(mss, "mss")
        with factory() as sct:
            mons = list(sct.monitors)
    except Exception:
        return [(1, "Monitor principal")]

    out: list[tuple[int, str]] = []
    for i, m in enumerate(mons):
        w, h = int(m.get("width", 0)), int(m.get("height", 0))
        if i == 0:
            # mons incluye el virtual en [0]; hay >1 físico si len(mons) > 2
            if len(mons) > 2:
                out.append((0, f"Todos los monitores ({w}×{h})"))
        else:
            out.append((i, f"Monitor {i} — {w}×{h}"))

    if not out:
        out.append((1, "Monitor principal"))
    return out
