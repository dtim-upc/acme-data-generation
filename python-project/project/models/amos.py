

__doc__ = """Classes used to populate the AMOS schema. 

The tables in the database don't have primary keys set, and in these 
models they use a PK candidate as for the requirements of the SQLAlchemy
modeling API. 

Read more about this in https://docs.sqlalchemy.org/en/13/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key"""


__proto_CREATE__="""-------------------------------------------------------------------------- AMOS

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