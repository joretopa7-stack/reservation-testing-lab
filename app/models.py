"""Modelo de datos del dominio de reservas."""

from dataclasses import dataclass
from datetime import date, time


@dataclass
class Reservation:
    customer_name: str
    service: str
    duration: int
    reservation_date: date
    reservation_time: time
    status: str
    confirmation_code: str
