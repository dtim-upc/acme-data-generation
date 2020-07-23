# coding: utf-8
import typing as T

import sqlalchemy as sa

from . import Base
from .mixins import ReprMixin, GhostIdMixin

__doc__ = """Classes used to populate the AIMS schema. 

The tables in the database don't have primary keys set, and in these 
models they use a PK candidate as for the requirements of the SQLAlchemy
modeling API. 

Read more about this in https://docs.sqlalchemy.org/en/13/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key"""

__proto_CREATE__ = """
----------------------  AIMS

CREATE TYPE SlotKind AS ENUM ('Flight', 'Maintenance', 'Buffer', 'Spare');

CREATE TABLE "AIMS".Slots (
	aircraftRegistration sa.CHAR(6) NOT NULL,
	scheduledDeparture TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	scheduledArrival TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	kind SlotKind NOT NULL);


CREATE TABLE "AIMS".Flights (
	flightID sa.CHAR(26) NOT NULL, -- Date-Origin-Destination-FlightNumber-AircraftRegistration -> 6+1+3+1+3+1+4+1+6
	departureAirport sa.CHAR(3) NOT NULL,
	arrivalAirport sa.CHAR(3) NOT NULL,
	actualDeparture TIMESTAMP WITHOUT TIME ZONE,
	actualArrival TIMESTAMP WITHOUT TIME ZONE,
	cancelled BOOLEAN,
	delayCode sa.CHAR(2), -- IATA code, 2 digits
	passengers SMALLINT,
	cabinCrew SMALLINT, 
	flightCrew SMALLINT 
) INHERITS ("AIMS".Slots);

CREATE TABLE "AIMS".Maintenance (
	programmed boolean NOT NULL
) INHERITS ("AIMS".Slots);"""


class AIMSMixin(object):
    __table_args__ = {"schema": "AIMS"}


class SlotsMixin(object):
    aircraftregistration = sa.Column("aircraftregistration", sa.CHAR(6), nullable=False)
    scheduleddeparture = sa.Column("scheduleddeparture", sa.DateTime, nullable=False)
    scheduledarrival = sa.Column("scheduledarrival", sa.DateTime, nullable=False)
    kind = sa.Column(
        "kind",
        sa.Enum("Flight", "Maintenance", "Buffer", "Spare", name="slotkind"),
        nullable=False,
    )


class Flight(Base, SlotsMixin, AIMSMixin):
    __tablename__ = "flights"

    flightid = sa.Column("flightid", sa.CHAR(26), nullable=False, primary_key=True)
    departureairport = sa.Column("departureairport", sa.CHAR(3), nullable=False)
    arrivalairport = sa.Column("arrivalairport", sa.CHAR(3), nullable=False)
    actualdeparture = sa.Column("actualdeparture", sa.DateTime)
    actualarrival = sa.Column("actualarrival", sa.DateTime)
    cancelled = sa.Column("cancelled", sa.Boolean)
    delaycode = sa.Column("delaycode", sa.CHAR(2))
    passengers = sa.Column("passengers", sa.SmallInteger)
    cabincrew = sa.Column("cabincrew", sa.SmallInteger)
    flightcrew = sa.Column("flightcrew", sa.SmallInteger)


class Maintenance(Base, SlotsMixin, GhostIdMixin, AIMSMixin):
    __tablename__ = "maintenance"
    programmed = sa.Column("programmed", sa.Boolean, nullable=False)


class Slot(Base, SlotsMixin, GhostIdMixin, AIMSMixin):
    __tablename__ = "slots"
