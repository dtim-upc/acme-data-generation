import typing as T
from datetime import datetime, timedelta
import attr


@attr.s(auto_attribs=True)
class Workpackage(object):
    workpackageid: T.Optional[int]
    executiondatetime: T.Optional[datetime]
    executionplace: T.Optional[str]


@attr.s(auto_attribs=True)
class Attachment(object):
    file: T.Optional[str]
    event: T.Optional[str]


@attr.s(auto_attribs=True)
class WorkOrder(object):
    workorderid: T.Optional[int]
    aircraftregistration: T.Optional[str]
    executiondatetime: T.Optional[datetime]
    executionplace: T.Optional[str]
    workpackage: T.Optional[int]
    kind: T.Optional[str]


@attr.s(auto_attribs=True)
class ForecastedOrder(WorkOrder):
    deadline: T.Optional[datetime]
    planned: T.Optional[datetime]
    frequency: T.Optional[int]
    frequencyunits: T.Optional[str]
    forecastedmanhours: T.Optional[int]


@attr.s(auto_attribs=True)
class TechnicalLogbookOrder(WorkOrder):
    reporteurclass: T.Optional[str]
    reporteurid: T.Optional[int]
    reportingdatetime: T.Optional[datetime]
    due: T.Optional[datetime]
    deferred: T.Optional[bool]
    mel: T.Optional[str]


@attr.s(auto_attribs=True)
class MaintenanceEvent(object):
    maintenanceid: T.Optional[str]
    aircraftregistration: T.Optional[str]
    airport: T.Optional[str]
    subsystem: T.Optional[str]
    starttime: T.Optional[datetime]
    duration: T.Optional[timedelta]
    kind: T.Optional[str]


@attr.s(auto_attribs=True)
class OperationInterruption(MaintenanceEvent):
    flightid: T.Optional[str]
    departure: T.Optional[datetime]
    delaycode: T.Optional[str]

