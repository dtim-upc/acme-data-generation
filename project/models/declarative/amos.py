# coding: utf-8

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INTERVAL, UUID
from sqlalchemy.sql.expression import case
from project.models.declarative.mixins import UtilsMixin, RowIdMixin


__doc__ = """Classes used to populate the AMOS schema. 

The tables in the database don't have primary keys set, and in these 
models they use a PK candidate as for the requirements of the SQLAlchemy
modeling API. 

Read more about this in https://docs.sqlalchemy.org/en/13/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key"""


Base = declarative_base()

# https://stackoverflow.com/a/22212214/5819113
sa.event.listen(
    Base.metadata,
    "before_create",
    sa.DDL('CREATE SCHEMA IF NOT EXISTS "AMOS"'),
)

sa.event.listen(
    Base.metadata,
    "after_drop",
    sa.DDL('DROP SCHEMA IF EXISTS "AMOS" CASCADE'),
)


__proto_CREATE__ = """-------------------------------------------------------------------------- AMOS

CREATE TABLE "AMOS".WorkPackages (
    workPackageID INT,
    executionDate DATE,
    executionPlace CHAR(3)
);

CREATE TYPE WorkOrderKind AS ENUM ('Forecast', 'TechnicalLogBook');

CREATE TABLE "AMOS".WorkOrders (
    workOrderID INT,
    aircraftRegistration CHAR(6) NOT NULL,
    executionDate DATE,
    executionPlace CHAR(3),
    workPackage INT,
    kind WorkOrderKind NOT NULL
);

CREATE TYPE FrequencyUnitsKind AS ENUM ('Flights', 'Days', 'Miles');

CREATE TABLE "AMOS".ForecastedOrders (
    deadline DATE NOT NULL,
    planned DATE NOT NULL,
    frequency SMALLINT NOT NULL,
    frequencyUnits FrequencyUnitsKind NOT NULL,
    forecastedManHours SMALLINT NOT NULL
) INHERITS ("AMOS".WorkOrders);

CREATE TYPE ReportKind AS ENUM ('PIREP', 'MAREP'); 
CREATE TYPE MELCathegory AS ENUM ('A', 'B', 'C', 'D');

CREATE TABLE "AMOS".TechnicalLogBookOrders (
    reporteurClass ReportKind NOT NULL,
    reporteurID SMALLINT NOT NULL,
    reportingDate DATE NOT NULL,
    due DATE,
    deferred BOOLEAN,
    MEL MELCathegory
) INHERITS ("AMOS".WorkOrders);

CREATE TYPE MaintenanceEventKind AS ENUM ('Delay', 'Safety', 'AircraftOnGround', 'Maintenance', 'Revision');

CREATE TABLE "AMOS".MaintenanceEvents (
    maintenanceID CHAR(30), 
    aircraftRegistration CHAR(6) NOT NULL,
    airport CHAR(3), 
    subsystem CHAR(4), 
    startTime TIMESTAMP WITHOUT TIME ZONE,
    duration INTERVAL,
    kind MaintenanceEventKind NOT NULL
);

CREATE TABLE "AMOS".OperationInterruption (
    flightID CHAR(22) NOT NULL,
    departure DATE NOT NULL,
    delayCode CHAR(2)
) INHERITS ("AMOS".MaintenanceEvents);

CREATE TABLE "AMOS".Attachments (
    file UUID,
    event CHAR(30) NOT NULL
);
"""


class Attachment(Base):

    __tablename__ = "attachments"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column("id", sa.Integer, primary_key=True)

    file = sa.Column("file", UUID)
    event = sa.Column("event", sa.CHAR(30), nullable=False)


class Workpackage(Base):
    __tablename__ = "workpackages"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column("id", sa.Integer, primary_key=True)

    workpackageid = sa.Column("workpackageid", sa.Integer)
    executiondate = sa.Column("executiondate", sa.Date)
    executionplace = sa.Column("executionplace", sa.CHAR(3))


class MaintenanceEvent(Base, UtilsMixin):
    __tablename__ = "maintenanceevents"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column("id", sa.Integer, primary_key=True)

    maintenanceid = sa.Column("maintenanceid", sa.CHAR(30))
    aircraftregistration = sa.Column("aircraftregistration", sa.CHAR(6), nullable=False)
    airport = sa.Column("airport", sa.CHAR(3))
    subsystem = sa.Column("subsystem", sa.CHAR(4))
    starttime = sa.Column("starttime", sa.DateTime)
    duration = sa.Column("duration", INTERVAL)
    kind = sa.Column(
        "kind",
        sa.Enum(
            "Delay",
            "Safety",
            "AircraftOnGround",
            "Maintenance",
            "Revision",
            name="maintenanceeventkind",
        ),
        nullable=False,
    )

    __mapper_args__ = {
        "polymorphic_on": case(
            [
                (kind.in_(("Delay", "Safety")), "OperationalInterruption"),
            ],
            else_="MaintenanceEvent",
        ),
        "polymorphic_identity": "MaintenanceEvent",
    }

    @classmethod
    def from_child(cls, obj):
        return cls(
            maintenanceid=obj.maintenanceid,
            aircraftregistration=obj.aircraftregistration,
            airport=obj.airport,
            subsystem=obj.subsystem,
            starttime=obj.starttime,
            duration=obj.duration,
            kind=obj.kind,
        )


class OperationalInterruption(MaintenanceEvent):
    __tablename__ = "operationinterruption"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column(
        "id", sa.Integer, sa.ForeignKey("AMOS.maintenanceevents.id"), primary_key=True
    )

    flightid = sa.Column("flightid", sa.CHAR(26), nullable=False)
    departure = sa.Column("departure", sa.Date, nullable=False)
    delaycode = sa.Column("delaycode", sa.CHAR(2))

    __mapper_args__ = {"polymorphic_identity": "OperationalInterruption"}


class WorkOrder(Base, UtilsMixin):
    __tablename__ = "workorders"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column("id", sa.Integer, primary_key=True)

    workorderid = sa.Column("workorderid", sa.Integer)
    aircraftregistration = sa.Column("aircraftregistration", sa.CHAR(6), nullable=False)
    executiondate = sa.Column("executiondate", sa.Date)
    executionplace = sa.Column("executionplace", sa.CHAR(3))
    workpackage = sa.Column("workpackage", sa.Integer)
    kind = sa.Column(
        "kind",
        sa.Enum("Forecast", "TechnicalLogBook", name="workorderkind"),
        nullable=False,
    )

    __mapper_args__ = {"polymorphic_on": kind, "polymorphic_identity": "WorkOrder"}

    @classmethod
    def from_child(cls, obj):
        return cls(
            workorderid=obj.workorderid,
            aircraftregistration=obj.aircraftregistration,
            executiondate=obj.executiondate,
            executionplace=obj.executionplace,
            workpackage=obj.workpackage,
            kind=obj.kind,
        )


class TechnicalLogbookOrder(WorkOrder):

    __tablename__ = "technicallogbookorders"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column(
        "id", sa.Integer, sa.ForeignKey("AMOS.workorders.id"), primary_key=True
    )

    reporteurclass = sa.Column(
        "reporteurclass",
        sa.Enum("PIREP", "MAREP", name="reportkind"),
        nullable=False,
    )

    reporteurid = sa.Column("reporteurid", sa.SmallInteger, nullable=False)
    reportingdate = sa.Column("reportingdate", sa.Date, nullable=False)
    due = sa.Column("due", sa.Date)
    deferred = sa.Column("deferred", sa.Boolean)
    mel = sa.Column("mel", sa.Enum("A", "B", "C", "D", name="melcathegory"))

    __mapper_args__ = {"polymorphic_identity": "TechnicalLogBook"}


class ForecastedOrder(WorkOrder):
    __tablename__ = "forecastedorders"
    __table_args__ = {"schema": "AMOS"}

    # This id is not meaningful at a domain level
    rowid = sa.Column(
        "id", sa.Integer, sa.ForeignKey("AMOS.workorders.id"), primary_key=True
    )

    deadline = sa.Column("deadline", sa.Date, nullable=False)
    planned = sa.Column("planned", sa.Date, nullable=False)
    frequency = sa.Column("frequency", sa.SmallInteger, nullable=False)
    frequencyunits = sa.Column(
        "frequencyunits",
        sa.Enum("Flights", "Days", "Miles", name="frequencyunitskind"),
        nullable=False,
    )
    forecastedmanhours = sa.Column(
        "forecastedmanhours", sa.SmallInteger, nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": "Forecast"}
