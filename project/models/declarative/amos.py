# coding: utf-8

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INTERVAL, UUID
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


class AMOSMixin(UtilsMixin):
    __table_args__ = {"schema": "AMOS"}


class Attachment(Base, RowIdMixin, AMOSMixin):
    __tablename__ = "attachments"
    file = sa.Column("file", UUID)
    event = sa.Column("event", sa.CHAR(30), nullable=False)


class Workpackage(Base, RowIdMixin, AMOSMixin):
    __tablename__ = "workpackages"
    workpackageid = sa.Column("workpackageid", sa.Integer)
    executiondate = sa.Column("executiondate", sa.Date)
    executionplace = sa.Column("executionplace", sa.CHAR(3))


class MaintenanceEventMixin(object):

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


class MaintenanceEvent(Base, RowIdMixin, MaintenanceEventMixin, AMOSMixin):
    __tablename__ = "maintenanceevents"


class OperationalInterruption(Base, RowIdMixin, MaintenanceEventMixin, AMOSMixin):
    __tablename__ = "operationinterruption"

    # TODO: confirm that
    # in the given sql for this table, `flightid` is of length 22. If the business rule R13 is hold, then
    # an operational interruption should have the same flightid, which is of length 26.
    flightid = sa.Column("flightid", sa.CHAR(26), nullable=False)
    departure = sa.Column("departure", sa.Date, nullable=False)
    delaycode = sa.Column("delaycode", sa.CHAR(2))


class WorkOrderMixin(object):

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


class WorkOrder(Base, RowIdMixin, WorkOrderMixin, AMOSMixin):
    __tablename__ = "workorders"


class TechnicalLogbookOrder(Base, RowIdMixin, WorkOrderMixin, AMOSMixin):
    __tablename__ = "technicallogbookorders"

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


class ForecastedOrder(Base, RowIdMixin, WorkOrderMixin, AMOSMixin):
    __tablename__ = "forecastedorders"

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
