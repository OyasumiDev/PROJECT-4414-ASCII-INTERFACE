"""
i_observer.py — Protocolos para el patrón Observer.

Define dos interfaces estructurales (via typing.Protocol):
    - IObserver   : cualquier objeto que pueda recibir notificaciones.
    - IObservable : cualquier objeto que pueda emitir notificaciones.

Al ser Protocols, no requieren herencia explícita; cualquier clase que
implemente los métodos correspondientes satisface automáticamente la interfaz
(duck-typing estructural de PEP 544).
"""

from typing import Protocol, Any


class IObserver(Protocol):
    """Contrato para objetos que reaccionan a eventos notificados por un Observable."""

    def update(self, data: Any) -> None:
        """
        Recibe una notificación con los datos del evento.

        Args:
            data: payload del evento; el tipo concreto depende del Observable.
        """
        ...


class IObservable(Protocol):
    """Contrato para objetos que emiten eventos a una lista de observadores."""

    def subscribe(self, observer: IObserver) -> None:
        """Registra un observador para recibir notificaciones futuras."""
        ...

    def notify(self, data: Any) -> None:
        """Emite un evento a todos los observadores registrados."""
        ...
