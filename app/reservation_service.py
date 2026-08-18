"""Servicio de reservas: coordina validadores, repositorio y generación
del código de confirmación, sin depender de FastAPI ni de una base de
datos real.
"""

from datetime import date
from typing import Callable

from app.exceptions import DuplicateReservationError
from app.models import Reservation
from app.repositories import InMemoryReservationRepository
from app.validators import (
    validate_customer_name,
    validate_service,
    validate_duration,
    validate_reservation_date,
    validate_reservation_time,
)


class ReservationService:
    def __init__(
        self,
        repository: InMemoryReservationRepository,
        confirmation_code_generator: Callable[[], str],
    ):
        self.repository = repository
        self.confirmation_code_generator = confirmation_code_generator

    def create(self, data: dict, current_date: date) -> Reservation:
        """Aplica todas las reglas de negocio y crea la reserva.

        Si cualquier validación falla, la excepción correspondiente se
        propaga y no se guarda ningún dato en el repositorio.
        """
        customer_name = validate_customer_name(data["customer_name"])
        service = validate_service(data["service"])
        duration = validate_duration(data["duration"])
        reservation_date = validate_reservation_date(
            data["reservation_date"], current_date
        )
        reservation_time = validate_reservation_time(
            data["reservation_time"], duration
        )

        # RN-08: no pueden existir dos reservas para la misma fecha y hora.
        if self.repository.exists(reservation_date, reservation_time):
            raise DuplicateReservationError(
                "Ya existe una reserva para esa fecha y hora."
            )

        # RN-10: el código de confirmación viene de una dependencia controlable.
        confirmation_code = self.confirmation_code_generator()

        reservation = Reservation(
            customer_name=customer_name,
            service=service,
            duration=duration,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            status="confirmed",  # RN-09
            confirmation_code=confirmation_code,
        )

        self.repository.add(reservation)
        return reservation
