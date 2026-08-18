from datetime import date, time

import pytest

from app.exceptions import (
    InvalidCustomerNameError,
    InvalidServiceError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidReservationTimeError,
)
from app.validators import (
    validate_customer_name,
    validate_service,
    validate_duration,
    validate_reservation_date,
    validate_reservation_time,
)


# ---------------------------------------------------------------------------
# RN-01: nombre del cliente
# ---------------------------------------------------------------------------

def test_validate_customer_name_strips_external_whitespace():
    # Arrange
    raw_name = "  Ana Torres  "

    # Act
    result = validate_customer_name(raw_name)

    # Assert
    assert result == "Ana Torres"


def test_validate_customer_name_rejects_names_shorter_than_three_chars():
    with pytest.raises(InvalidCustomerNameError):
        validate_customer_name("Jo")


def test_validate_customer_name_accepts_exactly_three_chars_after_trim():
    # Caso de frontera: exactamente 3 caracteres después de recortar espacios.
    assert validate_customer_name("  Ana  ") == "Ana"


# ---------------------------------------------------------------------------
# RN-02: servicio permitido
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw_service, expected",
    [
        pytest.param("asesoria", "asesoria", id="asesoria-minuscula"),
        pytest.param("  SOPORTE  ", "soporte", id="soporte-mayus-espacios"),
        pytest.param("Demostracion", "demostracion", id="demostracion-capitalizada"),
    ],
)
def test_validate_service_normalizes_allowed_services(raw_service, expected):
    assert validate_service(raw_service) == expected


def test_validate_service_rejects_unknown_service():
    with pytest.raises(InvalidServiceError):
        validate_service("consultoria")


# ---------------------------------------------------------------------------
# RN-03: duración permitida
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("duration", [pytest.param(30, id="30-min"), pytest.param(60, id="60-min")])
def test_validate_duration_accepts_allowed_values(duration):
    assert validate_duration(duration) == duration


@pytest.mark.parametrize(
    "invalid_duration",
    [pytest.param(15, id="15-min"), pytest.param(45, id="45-min"), pytest.param(90, id="90-min")],
)
def test_validate_duration_rejects_disallowed_values(invalid_duration):
    with pytest.raises(InvalidDurationError):
        validate_duration(invalid_duration)


# ---------------------------------------------------------------------------
# RN-04 y RN-05: fecha de la reserva
# ---------------------------------------------------------------------------

def test_validate_reservation_date_accepts_future_weekday(current_date):
    # martes 18 de agosto de 2026, un día hábil futuro respecto a current_date
    reservation_date = date(2026, 8, 18)

    assert validate_reservation_date(reservation_date, current_date) == reservation_date


def test_validate_reservation_date_accepts_the_current_date_itself(current_date):
    # Caso de frontera: la reserva es exactamente hoy (lunes hábil).
    assert validate_reservation_date(current_date, current_date) == current_date


def test_validate_reservation_date_rejects_past_date(current_date):
    past_date = date(2026, 8, 10)  # anterior a current_date

    with pytest.raises(InvalidReservationDateError):
        validate_reservation_date(past_date, current_date)


@pytest.mark.parametrize(
    "weekend_date",
    [
        pytest.param(date(2026, 8, 22), id="sabado"),
        pytest.param(date(2026, 8, 23), id="domingo"),
    ],
)
def test_validate_reservation_date_rejects_weekend_dates(weekend_date, current_date):
    with pytest.raises(InvalidReservationDateError):
        validate_reservation_date(weekend_date, current_date)


# ---------------------------------------------------------------------------
# RN-06 y RN-07: horario de la reserva
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "reservation_time, duration",
    [
        pytest.param(time(8, 0), 30, id="apertura-exacta"),
        pytest.param(time(12, 0), 60, id="mediodia"),
        pytest.param(time(16, 30), 30, id="ultimo-bloque-30-min"),
        pytest.param(time(16, 0), 60, id="ultimo-bloque-60-min"),
    ],
)
def test_validate_reservation_time_accepts_valid_slots(reservation_time, duration):
    assert validate_reservation_time(reservation_time, duration) == reservation_time


def test_validate_reservation_time_rejects_time_before_opening():
    with pytest.raises(InvalidReservationTimeError):
        validate_reservation_time(time(7, 59), 30)


@pytest.mark.parametrize(
    "reservation_time, duration",
    [
        pytest.param(time(16, 31), 30, id="termina-un-minuto-tarde"),
        pytest.param(time(16, 30), 60, id="termina-despues-de-cierre"),
        pytest.param(time(17, 0), 30, id="inicia-en-hora-de-cierre"),
    ],
)
def test_validate_reservation_time_rejects_slots_ending_after_closing(reservation_time, duration):
    with pytest.raises(InvalidReservationTimeError):
        validate_reservation_time(reservation_time, duration)
