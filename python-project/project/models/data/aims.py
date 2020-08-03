import typing as T
from faker import Faker
from datetime import datetime
from pydantic import BaseModel

from project.providers import AirportProvider

fake = Faker()
fake.add_provider(AirportProvider)


class Slot(BaseModel):
    aircraftregistration: str
    scheduleddeparture: str
    scheduledarrival: str
    kind: str


class Flight(Slot):
    flightid: str
    departureairport: str
    arrivalairport: str
    actualdeparture: datetime
    actualarrival: datetime
    cancelled: bool
    delaycode: str
    passengers: int
    cabincrew: int
    flightcrew: int


class Maintenance(Slot):
    programmed: bool
