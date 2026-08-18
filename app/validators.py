"""Validadores de las reglas de negocio del sistema de reservas.

Cada función tiene una única responsabilidad, no depende de FastAPI ni de
una base de datos, y recibe explícitamente cualquier dato "externo" (como
la fecha actual) para que las pruebas puedan controlarlo por completo.
"""

from datetime import date, time

from app.exceptions import (
    InvalidCustomerNameError,
    InvalidServiceError,
    InvalidDurationError,
    InvalidReservationDateError,
    InvalidReservationTimeError,
)

# RN-02: servicios permitidos.
ALLOWED_SERVICES = ("asesoria", "soporte", "demostracion")

# RN-03: duraciones permitidas, en minutos.
ALLOWED_DURATIONS = (30, 60)

# RN-06: el horario de atención inicia a las 08:00.
OPENING_TIME = time(8, 0)

# RN-07: la reserva debe finalizar máximo a las 17:00.
CLOSING_TIME = time(17, 0)

# RN-05: días hábiles (lunes=0 ... domingo=6).
WEEKEND_DAYS = (5, 6)


def validate_customer_name(customer_name: str) -> str:
    """RN-01: el nombre debe tener mínimo 3 caracteres tras recortar espacios."""
    normalized_name = customer_name.strip()

    if len(normalized_name) < 3:
        raise InvalidCustomerNameError(
            "El nombre del cliente debe tener al menos 3 caracteres."
        )
    return normalized_name


def validate_service(service: str) -> str:
    """RN-02: normaliza el servicio y valida que esté permitido."""
    normalized_service = service.strip().lower()

    if normalized_service not in ALLOWED_SERVICES:
        raise InvalidServiceError(
            f"El servicio debe ser uno de {ALLOWED_SERVICES}."
        )
    return normalized_service


def validate_duration(duration: int) -> int:
    """RN-03: la duración debe ser 30 o 60 minutos."""
    if duration not in ALLOWED_DURATIONS:
        raise InvalidDurationError(
            f"La duración debe ser una de {ALLOWED_DURATIONS} minutos."
        )
    return duration


def validate_reservation_date(reservation_date: date, current_date: date) -> date:
    """RN-04 y RN-05: la fecha no puede ser pasada ni caer en fin de semana.

    `current_date` se recibe como parámetro (en vez de usar date.today())
    para que las pruebas controlen siempre el "hoy" de referencia.
    """
    if reservation_date < current_date:
        raise InvalidReservationDateError(
            "No se puede crear una reserva para una fecha anterior a la fecha actual."
        )

    if reservation_date.weekday() in WEEKEND_DAYS:
        raise InvalidReservationDateError(
            "Solo se permiten reservas de lunes a viernes."
        )

    return reservation_date


def validate_reservation_time(reservation_time: time, duration: int) -> time:
    """RN-06 y RN-07: valida hora de apertura y hora máxima de finalización."""
    if reservation_time < OPENING_TIME:
        raise InvalidReservationTimeError(
            f"El horario de atención inicia a las {OPENING_TIME.strftime('%H:%M')}."
        )

    start_minutes = reservation_time.hour * 60 + reservation_time.minute
    end_minutes = start_minutes + duration
    closing_minutes = CLOSING_TIME.hour * 60 + CLOSING_TIME.minute

    if end_minutes > closing_minutes:
        raise InvalidReservationTimeError(
            f"La reserva debe finalizar máximo a las {CLOSING_TIME.strftime('%H:%M')}."
        )

    return reservation_time
