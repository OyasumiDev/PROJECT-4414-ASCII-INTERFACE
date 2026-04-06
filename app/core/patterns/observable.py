"""
observable.py — Implementación genérica del patrón Observer.

Permite que cualquier objeto notifique a múltiples suscriptores cuando
ocurre un cambio, desacoplando al emisor de sus receptores.

Uso típico:
    class MiFuente(Observable):
        def hacer_algo(self):
            self.notify(datos)

    clase MiObservador:
        def update(self, data): ...

    fuente = MiFuente()
    fuente.subscribe(MiObservador())
    fuente.hacer_algo()  # llama a update() en todos los suscritos
"""

from app.core.interfaces.i_observer import IObserver
from typing import Any


class Observable:
    """
    Clase base para objetos que emiten eventos a una lista de observadores.

    Los observadores deben implementar la interfaz IObserver (método `update`).
    """

    def __init__(self):
        self._observers: list[IObserver] = []

    def subscribe(self, observer: IObserver) -> None:
        """Registra un observador para recibir notificaciones futuras."""
        self._observers.append(observer)

    def unsubscribe(self, observer: IObserver) -> None:
        """Elimina un observador previamente registrado."""
        self._observers.remove(observer)

    def notify(self, data: Any) -> None:
        """Llama a `update(data)` en cada observador registrado."""
        for observer in self._observers:
            observer.update(data)
