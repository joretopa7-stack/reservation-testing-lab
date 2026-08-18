"""Fixtures compartidas por toda la suite de pruebas.

Ninguna fixture depende del día real en que se ejecuten las pruebas: la
fecha de referencia siempre es fija y conocida.
"""

from datetime import date, time

import pytest

from app.repositories import InMemoryReservationRepository
from app.reservation_service import ReservationService


@pytest.fixture
def current_date() -> date:
    """Fecha 'actual' fija y conocida: lunes 17 de agosto de 2026."""
    return date(2026, 8, 17)


@pytest.fixture
def valid_reservation_data(current_date) -> dict:
    """Diccionario con datos válidos de reserva, listo para usarse en create()."""
    return {
        "customer_name": "  Ana Torres  ",
        "service": "  Asesoria  ",
        "duration": 30,
        "reservation_date": date(2026, 8, 18),  # martes, día hábil futuro
        "reservation_time": time(9, 0),
    }


@pytest.fixture
def repository() -> InMemoryReservationRepository:
    """Instancia nueva del repositorio en memoria para cada prueba."""
    return InMemoryReservationRepository()


@pytest.fixture
def confirmation_code_generator():
    """Generador determinista de códigos de confirmación.

    No usa valores aleatorios: siempre entrega el mismo código fijo, para
    que las pruebas puedan comprobar exactamente qué llegó al resultado.
    """
    return lambda: "CONF-0001"


@pytest.fixture
def reservation_service(repository, confirmation_code_generator) -> ReservationService:
    """Servicio de reservas construido con dependencias controlables."""
    return ReservationService(
        repository=repository,
        confirmation_code_generator=confirmation_code_generator,
    )
