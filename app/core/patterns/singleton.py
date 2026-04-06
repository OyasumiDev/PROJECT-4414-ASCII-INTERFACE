"""
singleton.py — Metaclase que implementa el patrón Singleton.

Cualquier clase que use `metaclass=SingletonMeta` garantiza que solo existirá
una única instancia durante toda la vida del proceso. Las llamadas sucesivas a
su constructor devuelven siempre el mismo objeto ya creado.

Uso:
    class MiClase(metaclass=SingletonMeta):
        ...

    a = MiClase()
    b = MiClase()
    assert a is b  # True
"""


class SingletonMeta(type):
    """
    Metaclase Singleton genérica.

    Mantiene un diccionario `_instances` a nivel de metaclase que almacena una
    instancia por cada clase que la use. La primera llamada a `__call__` crea
    la instancia; las siguientes devuelven la ya existente sin volver a invocar
    `__init__`.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Devuelve la instancia existente o la crea si es la primera vez."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
