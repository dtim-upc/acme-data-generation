import typing as T
from datetime import datetime, timedelta
from pydantic import BaseModel


class Workpackage(BaseModel):
    workpackageid: int
    executiondatetime: datetime
    executionplace: str


class Attachment(BaseModel):
    file: str
    event: str


class WorkOrder(BaseModel):
    workorderid: int
    aircraftregistration: str
    executiondatetime: datetime
    executionplace: str
    workpackage: int
    kind: T.Tuple[str]


class ForecastedOrder(WorkOrder):
    deadline: datetime
    planned: datetime
    frequency: int
    frequencyunits: T.Tuple[str]
    forecastedmanhours: int


class TechnicalLogbookOrder(WorkOrder):
    reporteurclass: T.Tuple[str]
    reporteurid: int
    reportingdatetime: datetime
    due: datetime
    deferred: bool
    mel: T.Tuple[str]


class MaintenanceEvent(BaseModel):

    maintenanceid: str
    aircraftregistration: str
    airport: str
    subsystem: str
    starttime: datetime
    duration: timedelta
    kind: T.Tuple[str]


class OperationInterruption(MaintenanceEvent):
    flightid: str
    departure: datetime
    delaycode: str

