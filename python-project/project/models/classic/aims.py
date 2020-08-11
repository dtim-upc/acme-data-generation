# coding: utf-8
from sqlalchemy import (
    Boolean,
    CHAR,
    Column,
    DateTime,
    Enum,
    MetaData,
    SmallInteger,
    Integer,
    Table,
)
from sqlalchemy import event, DDL
from sqlalchemy.orm import mapper
from project.models.data import aims

# these classes are not used, DO NOT IMPORT metadata!

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
    Column("rowid", Integer, primary_key=True),  # needed by the ORM
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
    Column("rowid", Integer, primary_key=True),  # needed by the ORM
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
    Column("rowid", Integer, primary_key=True),  # needed by the ORM
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


# ---------------------------------------------------------------------------- #
#                                   mappings                                   #
# ---------------------------------------------------------------------------- #

# see https://docs.sqlalchemy.org/en/13/orm/mapping_styles.html#classical-mappings

t_slots_mapping = mapper(aims.Slot, t_slots)
t_flights_mapping = mapper(aims.FlightSlot, t_flights)
t_maintenance = mapper(aims.MaintenanceSlot, t_maintenance)
