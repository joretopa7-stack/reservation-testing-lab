"""Excepciones del dominio de reservas.

Todas las excepciones de negocio heredan de ReservationError para que el
código que consuma este servicio (por ejemplo, una futura API FastAPI)
pueda capturarlas de forma genérica cuando lo necesite, sin perder la
posibilidad de distinguir cada caso específico.
"""


class ReservationError(Exception):
    """Excepción base para cualquier error del dominio de reservas."""


class InvalidCustomerNameError(ReservationError):
    """Se lanza cuando el nombre del cliente no cumple RN-01."""


class InvalidServiceError(ReservationError):
    """Se lanza cuando el servicio solicitado no cumple RN-02."""


class InvalidDurationError(ReservationError):
    """Se lanza cuando la duración solicitada no cumple RN-03."""


class InvalidReservationDateError(ReservationError):
    """Se lanza cuando la fecha de la reserva no cumple RN-04 o RN-05."""


class InvalidReservationTimeError(ReservationError):
    """Se lanza cuando el horario de la reserva no cumple RN-06 o RN-07."""


class DuplicateReservationError(ReservationError):
    """Se lanza cuando ya existe una reserva para la misma fecha y hora (RN-08)."""
