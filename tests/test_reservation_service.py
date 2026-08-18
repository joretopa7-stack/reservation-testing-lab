from datetime import date, time

import pytest

from app.exceptions import (
    InvalidCustomerNameError,
    InvalidServiceError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidReservationTimeError,
    DuplicateReservationError,
)


# ---------------------------------------------------------------------------
# Creación exitosa (RN-09, RN-10) y normalización
# ---------------------------------------------------------------------------

def test_create_valid_reservation_has_confirmed_status(
    reservation_service, valid_reservation_data, current_date
):
    # Act
    reservation = reservation_service.create(valid_reservation_data, current_date)

    # Assert
    assert reservation.status == "confirmed"


def test_create_valid_reservation_uses_injected_confirmation_code(
    reservation_service, valid_reservation_data, current_date
):
    reservation = reservation_service.create(valid_reservation_data, current_date)

    assert reservation.confirmation_code == "CONF-0001"


def test_create_normalizes_customer_name_and_service(
    reservation_service, valid_reservation_data, current_date
):
    reservation = reservation_service.create(valid_reservation_data, current_date)

    assert reservation.customer_name == "Ana Torres"
    assert reservation.service == "asesoria"


def test_create_stores_the_reservation_in_the_repository(
    reservation_service, repository, valid_reservation_data, current_date
):
    reservation_service.create(valid_reservation_data, current_date)

    stored_reservations = repository.list()
    assert len(stored_reservations) == 1
    assert stored_reservations[0].confirmation_code == "CONF-0001"


# ---------------------------------------------------------------------------
# RN-08: reserva duplicada
# ---------------------------------------------------------------------------

def test_create_rejects_duplicate_reservation_for_same_date_and_time(
    reservation_service, valid_reservation_data, current_date
):
    # Arrange: se crea la primera reserva exitosamente.
    reservation_service.create(valid_reservation_data, current_date)

    duplicate_data = dict(valid_reservation_data, customer_name="Otro Cliente")

    # Act / Assert
    with pytest.raises(DuplicateReservationError):
        reservation_service.create(duplicate_data, current_date)


def test_duplicate_reservation_attempt_does_not_add_a_second_record(
    reservation_service, repository, valid_reservation_data, current_date
):
    reservation_service.create(valid_reservation_data, current_date)

    duplicate_data = dict(valid_reservation_data, customer_name="Otro Cliente")
    with pytest.raises(DuplicateReservationError):
        reservation_service.create(duplicate_data, current_date)

    assert len(repository.list()) == 1


# ---------------------------------------------------------------------------
# No persistencia ante error de validación
# ---------------------------------------------------------------------------

def test_invalid_reservation_is_not_saved_in_repository(
    reservation_service, repository, valid_reservation_data, current_date
):
    invalid_data = dict(valid_reservation_data, customer_name="Jo")  # RN-01

    with pytest.raises(InvalidCustomerNameError):
        reservation_service.create(invalid_data, current_date)

    assert repository.list() == []


# ---------------------------------------------------------------------------
# Parametrización: varios escenarios inválidos, ninguno persiste datos
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "field, value, expected_exception",
    [
        pytest.param("customer_name", "Jo", InvalidCustomerNameError, id="nombre-muy-corto"),
        pytest.param("service", "consultoria", InvalidServiceError, id="servicio-no-permitido"),
        pytest.param("duration", 45, InvalidDurationError, id="duracion-no-permitida"),
        pytest.param(
            "reservation_date", date(2026, 8, 22), InvalidReservationDateError, id="fecha-en-fin-de-semana"
        ),
        pytest.param(
            "reservation_time", time(7, 0), InvalidReservationTimeError, id="hora-antes-de-apertura"
        ),
    ],
)
def test_create_rejects_invalid_data_for_each_business_rule(
    reservation_service, repository, valid_reservation_data, current_date,
    field, value, expected_exception,
):
    invalid_data = dict(valid_reservation_data, **{field: value})

    with pytest.raises(expected_exception):
        reservation_service.create(invalid_data, current_date)

    # Ninguna de estas reservas inválidas debe quedar almacenada.
    assert repository.list() == []


# ---------------------------------------------------------------------------
# Independencia entre pruebas
# ---------------------------------------------------------------------------

def test_repository_starts_empty_for_every_test(repository):
    assert repository.list() == []


def test_creating_a_reservation_in_one_test_does_not_leak_into_another(
    reservation_service, repository, valid_reservation_data, current_date
):
    # Si una prueba anterior hubiera dejado estado global, este repositorio
    # (nuevo, inyectado por fixture) ya estaría contaminado.
    assert repository.list() == []

    reservation_service.create(valid_reservation_data, current_date)

    assert len(repository.list()) == 1
