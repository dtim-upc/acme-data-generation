import typing as T
from faker import Faker
from datetime import datetime
import attr


@attr.s(auto_attribs=True)
class Slot(object):
    aircraftregistration: T.Optional[str]
    scheduleddeparture: T.Optional[str]
    scheduledarrival: T.Optional[str]
    kind: T.Optional[str]

    @classmethod
    def from_child(cls, obj):
        return cls(
            obj.aircraftregistration,
            obj.scheduleddeparture,
            obj.scheduledarrival,
            obj.kind,
        )


@attr.s(auto_attribs=True)
class FlightSlot(Slot):
    flightid: T.Optional[str]
    departureairport: T.Optional[str]
    arrivalairport: T.Optional[str]
    actualdeparture: T.Optional[datetime]
    actualarrival: T.Optional[datetime]
    cancelled: T.Optional[bool]
    delaycode: T.Optional[str]
    passengers: T.Optional[int]
    cabincrew: T.Optional[int]
    flightcrew: T.Optional[int]


@attr.s(auto_attribs=True)
class MaintenanceSlot(Slot):
    programmed: T.Optional[bool]
