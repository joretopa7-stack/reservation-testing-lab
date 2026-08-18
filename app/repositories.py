"""Repositorio en memoria para reservas.

Sustituye temporalmente una base de datos real. Cada instancia mantiene su
propia lista interna, por lo que dos instancias nunca comparten estado
(no se usan variables globales), lo cual permite que cada prueba reciba un
repositorio nuevo y vacío.
"""

from datetime import date, time


class InMemoryReservationRepository:
    def __init__(self):
        self._reservations = []

    def exists(self, reservation_date: date, reservation_time: time) -> bool:
        """RN-08: indica si ya hay una reserva para esa fecha y hora."""
        return any(
            reservation.reservation_date == reservation_date
            and reservation.reservation_time == reservation_time
            for reservation in self._reservations
        )

    def add(self, reservation) -> None:
        """Guarda una reserva en el repositorio."""
        self._reservations.append(reservation)

    def list(self) -> list:
        """Devuelve una copia de las reservas almacenadas."""
        return list(self._reservations)
