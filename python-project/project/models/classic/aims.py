# coding: utf-8
from sqlalchemy import (
    Boolean,
    CHAR,
    Column,
    DateTime,
    Enum,
    MetaData,
    SmallInteger,
    Table,
)
from sqlalchemy import event, DDL

metadata = MetaData()

# https://stackoverflow.com/a/22212214/5819113
event.listen(
    metadata, "before_create", DDL('CREATE SCHEMA IF NOT EXISTS "AIMS"'),
)

event.listen(
    metadata, "after_drop", DDL('DROP SCHEMA IF EXISTS "AIMS" CASCADE'),
)

t_flights = Table(
    "flights",
    metadata,
    Column("aircraftregistration", CHAR(6), nullable=False),
    Column("scheduleddeparture", DateTime, nullable=False),
    Column("scheduledarrival", DateTime, nullable=False),
    Column(
        "kind",
        Enum("Flight", "Maintenance", "Buffer", "Spare", name="slotkind"),
        nullable=False,
    ),
    Column("flightid", CHAR(26), nullable=False),
    Column("departureairport", CHAR(3), nullable=False),
    Column("arrivalairport", CHAR(3), nullable=False),
    Column("actualdeparture", DateTime),
    Column("actualarrival", DateTime),
    Column("cancelled", Boolean),
    Column("delaycode", CHAR(2)),
    Column("passengers", SmallInteger),
    Column("cabincrew", SmallInteger),
    Column("flightcrew", SmallInteger),
    schema="AIMS",
)


t_maintenance = Table(
    "maintenance",
    metadata,
    Column("aircraftregistration", CHAR(6), nullable=False),
    Column("scheduleddeparture", DateTime, nullable=False),
    Column("scheduledarrival", DateTime, nullable=False),
    Column(
        "kind",
        Enum("Flight", "Maintenance", "Buffer", "Spare", name="slotkind"),
        nullable=False,
    ),
    Column("programmed", Boolean, nullable=False),
    schema="AIMS",
)


t_slots = Table(
    "slots",
    metadata,
    Column("aircraftregistration", CHAR(6), nullable=False),
    Column("scheduleddeparture", DateTime, nullable=False),
    Column("scheduledarrival", DateTime, nullable=False),
    Column(
        "kind",
        Enum("Flight", "Maintenance", "Buffer", "Spare", name="slotkind"),
        nullable=False,
    ),
    schema="AIMS",
)
