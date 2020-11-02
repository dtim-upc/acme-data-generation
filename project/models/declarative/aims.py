# coding: utf-8
import typing as T

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.expression import case
from project.models.declarative.mixins import UtilsMixin, RowIdMixin
from datetime import datetime, timedelta

Base = declarative_base()

# https://stackoverflow.com/a/22212214/5819113
sa.event.listen(
    Base.metadata,
    "before_create",
    sa.DDL('CREATE SCHEMA IF NOT EXISTS "AIMS"'),
)

sa.event.listen(
    Base.metadata,
    "after_drop",
    sa.DDL('DROP SCHEMA IF EXISTS "AIMS" CASCADE'),
)

__doc__ = """Classes used to populate the AIMS schema. 

The tables in the database don't have primary keys set, and in these 
models they use a PK candidate as for the requirements of the SQLAlchemy
modeling API. 

Read more about this in https://docs.sqlalchemy.org/en/13/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key"""

__proto_CREATE__ = """
----------------------  AIMS

CREATE TYPE SlotKind AS ENUM ('Flight', 'Maintenance', 'Buffer', 'Spare');

CREATE TABLE "AIMS".Slots (
	aircraftRegistration CHAR(6) NOT NULL,
	scheduledDeparture TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	scheduledArrival TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	kind SlotKind NOT NULL);


CREATE TABLE "AIMS".Flights (
	flightID CHAR(26) NOT NULL, -- Date-Origin-Destination-FlightNumber-AircraftRegistration -> 6+1+3+1+3+1+4+1+6
	departureAirport CHAR(3) NOT NULL,
	arrivalAirport CHAR(3) NOT NULL,
	actualDeparture TIMESTAMP WITHOUT TIME ZONE,
	actualArrival TIMESTAMP WITHOUT TIME ZONE,
	cancelled BOOLEAN,
	delayCode CHAR(2), -- IATA code, 2 digits
	passengers SMALLINT,
	cabinCrew SMALLINT, 
	flightCrew SMALLINT 
) INHERITS ("AIMS".Slots);

CREATE TABLE "AIMS".Maintenance (
	programmed boolean NOT NULL
) INHERITS ("AIMS".Slots);"""


class Slot(Base, UtilsMixin):
    __tablename__ = "slots"
    __table_args__ = {"schema": "AIMS"}

    # just needed by the ORM
    rowid = sa.Column("id", sa.Integer, primary_key=True)

    aircraftregistration = sa.Column("aircraftregistration", sa.CHAR(6), nullable=False)
    scheduleddeparture = sa.Column("scheduleddeparture", sa.DateTime, nullable=False)
    scheduledarrival = sa.Column("scheduledarrival", sa.DateTime, nullable=False)
    kind = sa.Column(
        "kind",
        sa.Enum("Flight", "Maintenance", "Buffer", "Spare", name="slotkind"),
        nullable=False,
    )
    
    __mapper_args__ = {
        "polymorphic_on": case(
            [
                (kind == "Flight", "FlightSlot"),
                (kind == "Maintenance", "MaintenanceSlot"),
            ],
            else_="Slot",
        ),
        "polymorphic_identity": "Slot",
    }

    @classmethod
    def from_child(cls, obj):
        return cls(
            aircraftregistration=obj.aircraftregistration,
            scheduleddeparture=obj.scheduleddeparture,
            scheduledarrival=obj.scheduledarrival,
            kind=obj.kind,
        )


class FlightSlot(Slot):
    __tablename__ = "flights"
    __table_args__ = {"schema": "AIMS"}

    # just needed by the ORM
    rowid = sa.Column("id", sa.Integer, sa.ForeignKey("AIMS.slots.id"), primary_key=True)

    flightid: str = sa.Column("flightid", sa.CHAR(26), nullable=False)
    departureairport: str = sa.Column("departureairport", sa.CHAR(3), nullable=False)
    arrivalairport: str = sa.Column("arrivalairport", sa.CHAR(3), nullable=False)
    actualdeparture: datetime = sa.Column("actualdeparture", sa.DateTime)
    actualarrival: datetime = sa.Column("actualarrival", sa.DateTime)
    cancelled: bool = sa.Column("cancelled", sa.Boolean)
    delaycode: str = sa.Column("delaycode", sa.CHAR(2))
    passengers: int = sa.Column("passengers", sa.SmallInteger)
    cabincrew: int = sa.Column("cabincrew", sa.SmallInteger)
    flightcrew: int = sa.Column("flightcrew", sa.SmallInteger)

    __mapper_args__ = {"polymorphic_identity": "FlightSlot"}


class MaintenanceSlot(Slot):
    __tablename__ = "maintenance"
    __table_args__ = {"schema": "AIMS"}

    # just needed by the ORM
    rowid = sa.Column("id", sa.Integer, sa.ForeignKey("AIMS.slots.id"), primary_key=True)

    programmed: bool = sa.Column("programmed", sa.Boolean, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "MaintenanceSlot"}
