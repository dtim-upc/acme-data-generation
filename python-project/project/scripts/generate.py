import logging
import random
import typing as T
import datetime as dt
from pathlib import Path
from datetime import datetime
from uuid import UUID

from faker import Faker

from project.scripts.config import Config
from project.scripts.rules import mapping

fake = Faker()

Faker.seed(Config.SEED)
random.seed(Config.SEED)

logging.basicConfig(level=logging.DEBUG)  # use root logger


class AircraftGenerator:
    def __init__(self, config):
        super().__init__()
        self.config = config

    def _preallocate_array(self, size=None):

        if size is None:
            size = self.config.SIZE

        # means we need to allocate a nxd array, only 2d supported
        if isinstance(size, tuple):
            return [[None for _ in range(size[0])] for _ in range(size[1])]

        return [None] * size

    def create_fleet(self) -> T.Tuple:

        # self.fleet generation to be saved in aircraft-manufacturerinfo-lookup.csv
        for i in range(self.config.FLEET_SIZE):
            self.fleet[i] = self.config.REGPREFIX + "".join(random.sample(self.config.ALPHABET, 3))
            self.MSNs[i] = "MSN " + str(random.randrange(1000, 9000))
            k: int = random.randrange(0, len(self.config.AIRCRAFTMODELS))
            self.models[i] = self.config.AIRCRAFTMODELS[k]
            self.manufacturers[i] = self.config.AIRCRAFTMANUFACTURERS[k]

        logging.debug(self.fleet)
        logging.debug(self.models)
        logging.debug(self.MSNs)
        logging.debug(self.manufacturers)

        return self

    def create_aircraft_registrations(self, fleet=None) -> T.List[str]:

        # take a sample from fleet and create a list of aircraft registrations
        # g = Generator(config=Config) caveat: sample is without repetition!
        # TODO: check if repetition is needed

        self.aircraft_registrations: T.List[str] = random.choices(fleet or self.fleet, k=self.config.SIZE)

        logging.debug(self.aircraft_registrations)
        return self

    def create_timestamps(self):
        """Creates arrival,  departure, delayCode, canceled"""

        # populate arrays
        for i in range(self.config.SIZE):

            # produce random timestamp between two
            # dates and set scheduled departure from them
            rand_datetime: datetime = fake.date_time_between_dates(self.config.OFFSET, self.config.END)

            # craft scheduled_departure
            self.scheduled_departures[i] = rand_datetime

            # craft scheduled_arrival ocurring after N hours later
            self.scheduled_arrivals[i] = self.scheduled_departures[i] + dt.timedelta(hours=self.config.MAX_DUR)

            self.cancelled[i] = fake.pybool()

            # if it was cancelled, reflect that
            if self.cancelled[i]:
                self.delays[i] = 0
                self.delay_codes[i] = None
                self.actual_arrivals[i] = None
                self.actual_departures[i] = None
            else:  
                # if flight was not cancelled, then set delays, if any
                self.delays[i]: int = random.randrange(0, self.config.MAX_DELAY) # define a random delay in minutes

                # if delay ocurred, determine reason
                # if there are delays, then this flight goes to operational interruptions
                # TODO: this is rule R7
                if self.delays[i] > 0:
                    self.delay_codes[i] = random.choice(self.config.DELAYCODESOPTIONS)
                else:
                    self.delay_codes[i] = None

                # define actual departures and arrivals
                self.actual_departures[i]: datetime = self.scheduled_departures[i] + dt.timedelta(
                    minutes=self.delays[i]
                )

                self.actual_arrivals[i]: datetime = self.scheduled_arrivals[i] + dt.timedelta(
                    minutes=self.config.MAX_DELAY
                )

        return self

    def preallocate_arrays(self):
        # fmt: off
        self.fleet: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.MSNs: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.models: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.manufacturers: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)

        self.scheduled_departures: T.List[datetime] = self._preallocate_array()
        self.scheduled_arrivals: T.List[datetime] = self._preallocate_array()
        self.actual_departures: T.List[datetime] = self._preallocate_array()
        self.actual_arrivals: T.List[datetime] = self._preallocate_array()
        self.delays: T.List[int] = self._preallocate_array()
        self.cancelled: T.List[bool] = self._preallocate_array()
        self.delay_codes: T.List[str] = self._preallocate_array()

        # TODO: refactor this
        # slots kinds, origin and destination, passengers info
        self.slots_kinds: T.List[str] = self._preallocate_array()
        self.flight_ids: T.List[str] = self._preallocate_array()
        self.origin_dest: T.List[T.Tuple] = self._preallocate_array()

        # TODO: implement this line in python
        # HashMap<String, String> orgDestToFlightNo = new HashMap<String, String>();

        # to AIMS.flight
        self.passengers: T.List[int] = self._preallocate_array()
        self.cabin_crew: T.List[int] = self._preallocate_array()
        self.flight_crew: T.List[int] = self._preallocate_array()

        # to AIMS.maintenance
        self.programmed: T.List[bool] = self._preallocate_array()

        # to AIMS.maintenanceevents
        self.maintenance_id: T.List[str] = self._preallocate_array()
        self.airport_maintenance: T.List[str] = self._preallocate_array()
        self.subsystem: T.List[str] = self._preallocate_array()
        self.starttimes: T.List[dt.timedelta] = self._preallocate_array()

        # AMOS.maintenanceevents.interval
        self.days: T.List[int] = self._preallocate_array()
        self.hours: T.List[int] = self._preallocate_array()
        self.minutes: T.List[int] = self._preallocate_array()
        self.durations: T.List[str] = self._preallocate_array()

        # // AMOS.maintenanceevents.maintenancekind
        self.maintenance_kinds: T.List[str] = self._preallocate_array()

        # AMOS.operationinterruption
        self.departure: T.List[datetime] = self._preallocate_array()

        # AMOS.attachments
        self.attachment_files: T.List[T.List[str]] = self._preallocate_array(
            size=(
                self.config.MAX_ATTCH_SIZE,
                self.config.SIZE,
            )  # allocate an array with #SIZE arrays of size MAX_ATTCH_SIZE
        )

        self.attachment_events: T.List[T.List[str]] = self._preallocate_array(
            size=(
                self.config.MAX_ATTCH_SIZE,
                self.config.SIZE,
            )  # allocate an array with #SIZE arrays of size MAX_ATTCH_SIZE
        )

        # AMOS.workpackages variables
        self.work_package_ids: T.List[int] = self._preallocate_array()
        self.execution_dates: T.List[datetime] = self._preallocate_array()
        self.execution_places: T.List[str] = self._preallocate_array()

        # initialize arrays to store 1000 (i.e. SIZE) instances of AMOS.workorders
        self._wosize = (self.config.MAX_WORK_ORDERS, self.config.SIZE)

        self.workorder_ids: T.List[T.List[int]] = self._preallocate_array(self._wosize)
        self.workorder_aircraftregs: T.List[T.List[str]] = self._preallocate_array(self._wosize)
        self.workorder_executiondates: T.List[T.List[datetime]] = self._preallocate_array(self._wosize)
        self.workorder_executionplaces: T.List[T.List[str]] = self._preallocate_array(self._wosize)
        self.workorder_workpackageids: T.List[T.List[int]] = self._preallocate_array(self._wosize)
        self.workorder_workorderkinds: T.List[T.List[str]] = self._preallocate_array(self._wosize)
        self.workorder_deadlines: T.List[T.List[datetime]] = self._preallocate_array(self._wosize)
        self.workorder_planneddates: T.List[T.List[datetime]] = self._preallocate_array(self._wosize)
        self.workorder_frequencies: T.List[T.List[int]] = self._preallocate_array(self._wosize)
        self.workorder_frequencyunits: T.List[T.List[str]] = self._preallocate_array(self._wosize)
        self.workorder_forecastedmanhours: T.List[T.List[int]] = self._preallocate_array(self._wosize)
        self.workorder_reporteurclasses: T.List[T.List[str]] = self._preallocate_array(self._wosize)
        self.workorder_reporteurids: T.List[T.List[int]] = self._preallocate_array(self._wosize)
        self.workorder_duedates: T.List[T.List[datetime]] = self._preallocate_array(self._wosize)
        self.workorder_reportingdate: T.List[T.List[datetime]] = self._preallocate_array(self._wosize)
        self.workorder_deferreds: T.List[T.List[bool]] = self._preallocate_array(self._wosize)
        self.workorder_mels: T.List[T.List[str]] = self._preallocate_array(self._wosize)

    def populate_flights_maintenances(self):
        # populate data
        for i in range(self.config.SIZE):
            # pick a slotkind at random from "flight, maintenance"
            self.slots_kinds[i] = random.choice(self.config.SLOTKINDOPTIONS)

            # if slot kind is Maintenance, or if that flight presented delays, specify details
            # check
            if self.slots_kinds[i] == "Maintenance" or self.delays[i] > 0:

                self.programmed[i] = fake.pybool()  # AIMS.maintenance.programmed
                # TODO: this is rule R11
                self.airport_maintenance[i] = random.choice(self.config.AIRPORTCODES)  #  AMOS.maintenanceevents.airport
                # TODO: this is rule R6
                self.subsystem[i] = random.choice(self.config.ATACODES)  # AMOS.maintenanceevents.subsystem
                self.starttimes[i] = self.scheduled_departures[i]  # AMOS.maintenanceevents.starttimes
                self.maintenance_kinds[i] = random.choice(
                    self.config.MAINTENANCEEVENTOPTIONS
                )  # AMOS.maintenanceevents.kind

                # setup depending on the maintenance kind obtained
                if self.maintenance_kinds[i] == "Delay":
                    self.days[i] = random.randrange(60)

                elif self.maintenance_kinds[i] == "Safety":
                    self.days[i] = random.randrange(90)
                    self.hours[i] = random.randrange(24)
                    self.minutes[i] = random.randrange(60)

                elif self.maintenance_kinds[i] == "AircraftOnGround":
                    self.hours[i] = random.randrange(24)
                    self.minutes[i] = random.randrange(60)

                elif self.maintenance_kinds[i] == "Maintenance":
                    self.days[i] = random.randrange(1)
                    self.hours[i] = random.randrange(24)
                    self.minutes[i] = random.randrange(60)

                elif self.maintenance_kinds[i] == "Revision":
                    self.days[i] = random.randrange(31)
                    self.hours[i] = random.randrange(24)
                    self.minutes[i] = random.randrange(60)

                self.durations[i] = dt.timedelta(
                    days=self.days[i] or 0, 
                    hours=self.hours[i] or 0, 
                    minutes=self.minutes[i] or 0)

                # TODO: This is rule R3
                # TODO: resolve the line in Java: maintenanceID[i] = r.nextInt(SIZE - 250); // AMOS.maintenanceevents.maintenanceid
                self.maintenance_id[i] = "_".join([
                        str(random.randrange(self.config.SIZE)),
                        str(self.starttimes[i] + self.durations[i])]) # AMOS.maintenanceevents.maintenanceid
                
                # TODO: check why is this
                self.departure[i] = self.scheduled_departures[i]  # I think this is AMOS.maintenanceevents.departure

                # TODO: enforce rule R15-D through a configurable file
                rule_15_d = True
                if rule_15_d:
                    if self.durations[i] > dt.timedelta(days=1):
                        self.durations[i] = dt.timedelta(days=1)

                # AMOS.attachments
                for j in range(self.config.MAX_ATTCH_SIZE):
                    # TODO: this is rule R4: 
                    self.attachment_files[i][j] = fake.uuid4()
                    # TODO: this is rule R5: 
                    # event of an Attachement is a reference to maintenanceID of MaintenanceEvents 
                    # enforce it using a config
                    self.attachment_events[i][j] = self.maintenance_id[i] 

                # AMOS.workpackages
                # TODO: Implement rule R1
                self.work_package_ids[i] = random.randrange(self.config.SIZE)  # AMOS.workpackages.workpackageid
                self.execution_dates[i] = self.departure[i]  # AMOS.workpackages.executiondate
                self.execution_places[i] = self.airport_maintenance[i]  # AMOS.workpackages.executionplace

                # AMOS.workorders
                for j in range(self.config.MAX_WORK_ORDERS):
                    # TODO: Implement rule R2
                    self.workorder_ids[i][j] = random.randrange(self.config.SIZE)
                    self.workorder_aircraftregs[i][j] = self.aircraft_registrations[i]
                    self.workorder_executiondates[i][j] = self.departure[i]
                    self.workorder_executionplaces[i][j] = self.airport_maintenance[i]
                    self.workorder_workpackageids[i][j] = self.work_package_ids[i]
                    self.workorder_workorderkinds[i][j] = random.choice(self.config.WORKORDERKINDOPTIONS)

                    # in Java, these are used to produce dates.
                    # TODO: check what are these numbers (250-20, etc)
                    #
                    #                         Calendar c1 = Calendar.getInstance();
                    #                         c1.setTimeInMillis(departure[i].getTime());
                    #                         int dur = r.nextInt((250 - 20) + 1) + 20;
                    #                         c1.add(Calendar.DAY_OF_YEAR, dur);

                    #                         Calendar c2 = Calendar.getInstance();
                    #                         c2.setTimeInMillis(departure[i].getTime());
                    #                         dur = dur - r.nextInt((10 - 1) + 1) + 1;
                    #                         c2.add(Calendar.DAY_OF_YEAR, dur);

                    self.workorder_deadlines[i][j] = self.departure[i] + dt.timedelta(
                        days=(random.randrange((250 - 20) + 1) + 20)
                    )

                    self.workorder_planneddates[i][j] = self.departure[i] + dt.timedelta(
                        days=(random.randrange((10 - 1) + 1) + 1)
                    )
                    self.workorder_frequencyunits[i][j] = random.choice(self.config.FREQUENCYUNITSKINDOPTIONS)
                    self.workorder_frequencies[i][j] = random.randrange(100)
                    self.workorder_forecastedmanhours[i][j] = random.randrange(20)
                    self.workorder_reporteurclasses[i][j] = random.choice(self.config.REPORTKINDOPTIONS)
                    self.workorder_reporteurids[i][j] = random.randrange(500)
                    self.workorder_duedates[i][j] = self.workorder_deadlines[i][j]

                    self.workorder_deferreds[i][j] = fake.pybool()

                    # TODO: this is rule R10    
                    self.workorder_mels[i][j] = random.choice(self.config.MELCATEGORYOPTIONS)

                    _mel_mapping = {
                        "A": dt.timedelta(days=-3),
                        "B": dt.timedelta(days=-10),
                        "C": dt.timedelta(days=-30),
                        "D": dt.timedelta(days=-120),
                    }

                    # TODO: confirm why this has a default of -5 days
                    self.workorder_reportingdate[i][j] = self.workorder_duedates[i][j] + _mel_mapping.get(
                        self.workorder_mels[i][j], dt.timedelta(days=-5)
                    )
            else:
                # if no maintenance and no delays
                # construct flight
                flight_pair = Flight(
                    config=self.config,
                    scheduled_departure=self.scheduled_departures[i],
                    aircraft_registration=self.aircraft_registrations[i],
                )

                # TODO: don't know why is this necessary
                self.origin_dest[i] = flight_pair
                self.pair_number_mapping = {}
                self.pair_number_mapping[str(flight_pair)] = flight_pair.flight_number

                self.passengers[i] = flight_pair.passengers
                self.cabin_crew[i] = flight_pair.cabin_crew
                self.flight_crew[i] = flight_pair.flight_crew
                self.flight_ids[i] = flight_pair.flight_id

        return self

    def populate(self):
        # TODO: refactor this
        self.preallocate_arrays()
        self.create_fleet()
        self.create_aircraft_registrations()
        self.create_timestamps()
        self.populate_flights_maintenances()
        return self

    def get_flights(self, output: Path = None) -> T.Generator:
        output_flights = (
            [
                self.aircraft_registrations[i],
                self.scheduled_departures[i],
                self.scheduled_arrivals[i],
                self.slots_kinds[i],
                self.flight_ids[i], # TODO: this is rule R13-A
                self.origin_dest[i].orig,
                self.origin_dest[i].dest,
                self.actual_departures[i],
                self.actual_arrivals[i],
                self.cancelled[i],
                self.delay_codes[i],
                self.passengers[i],
                self.cabin_crew[i],
                self.flight_crew[i],
            ]
            for i in range(self.config.SIZE)
        )

        return output_flights

    def get_maintenances(self) -> T.Generator:
        output_maintenances = (
            [
                self.aircraft_registrations[i],
                self.scheduled_departures[i],
                self.scheduled_arrivals[i],
                self.slot_kinds[i],
                self.programmed[i],
            ]
            for i in range(self.config.SIZE)
        )
        return output_maintenances

    def get_operational_interruptions(self) -> T.Generator:
        # Data is already loaded in self
        # we will deal in generators to avoid processing
        # everything in memory.

        out = ([
                    self.maintenance_id[i], # 0
                    self.aircraft_registrations[i], # 1
                    self.airport_maintenance[i], # 2
                    self.subsystem[i], # 3
                    self.starttimes[i], # 4
                    self.durations[i], # 5
                    self.maintenance_kinds[i], # 6
                    # TODO: rule R13-B
                    self.flight_ids[i], # 7 
                    self.departure[i], # 8
                    self.delay_codes[i], # 9
                    # following are needed just to produce the output
                ] for i in range(self.config.SIZE))
        return out

    def get_attachments(self) -> T.Generator:
        
        return ([self.attachment_files[i][j], self.attachment_events[i][j]] 
                    for i in range(self.config.SIZE)
                    for j in range(self.config.MAX_ATTCH_SIZE))

    def get_workpackages(self) -> T.Generator:

        workpackages = ([
            self.work_package_ids[i],
            self.execution_dates[i],
            self.execution_places[i]] 
            for i in range(self.config.SIZE) 
            if self.slots_kinds[i] == "Maintenance" 
            or self.delays[i] > 0)
        
        return workpackages

    def get_forecasted_orders(self) -> T.Generator:
    
        forecasted_orders = ([
            self.workorder_ids[i][j],
            self.workorder_aircraftregs[i][j],
            self.workorder_executiondates[i][j],
            self.workorder_executionplaces[i][j],
            self.workorder_workpackageids[i][j],
            self.workorder_workorderkinds[i][j],
            self.workorder_deadlines[i][j],
            self.workorder_planneddates[i][j],
            self.workorder_frequencies[i][j],
            self.workorder_frequencyunits[i][j],
            self.workorder_forecastedmanhours[i][j],
            ] 
            for i in range(self.config.SIZE)
            for j in range(self.config.MAX_ATTCH_SIZE)
            if (self.slots_kinds[i] == "Maintenance" or self.delays[i] > 0) 
            and self.workorder_workorderkinds[i] == "Forecast")
        
        return forecasted_orders

    def get_tlb_orders(self, ) -> T.Generator:
    
        tlb_orders = ([
            self.workorder_ids[i][j],
            self.workorder_aircraftregs[i][j],
            self.workorder_executiondates[i][j],
            self.workorder_executionplaces[i][j],
            self.workorder_workpackageids[i][j],
            self.workorder_workorderkinds[i][j],
            self.workorder_reporteurclasses[i][j],
            self.workorder_reporteurids[i][j],
            self.workorder_planneddates[i][j],
            self.workorder_duedates[i][j],
            self.workorder_deferreds[i][j],
            self.workorder_mels[i][j],
            self.workorder_reportingdate[i][j]
            ]
            for i in range(self.config.SIZE)
            for j in range(self.config.MAX_ATTCH_SIZE)
            if (self.slots_kinds[i] == "Maintenance" or self.delays[i] > 0) 
            and self.workorder_workorderkinds[i] == "TechnicalLogBook")
        
        return tlb_orders


class Flight(object):
    def __init__(self, config: Config, scheduled_departure: datetime, aircraft_registration: str):
        self.route: T.List[str] = random.sample(config.AIRPORTCODES, k=2)
        self.orig: str = self.route[0]
        self.dest: str = self.route[1]
        self.flight_number = str(random.randrange(1000, 9999))
        self.passengers: int = random.randint(a=config.MIN_PAS, b=config.MAX_PAS)
        self.cabin_crew: int = random.randint(a=config.MIN_CCREW, b=config.MAX_CCREW)
        self.flight_crew: int = random.randint(a=config.MIN_FCREW, b=config.MAX_FCREW)

        # TODO: refactor code to remove these args and init them here
        self.scheduled_departure: datetime = scheduled_departure
        self.aircraft_registration: str = aircraft_registration

        # stfrtime uses here the format that was in the java code.
        # This date is not ISO 8601 compliant, but it could be set
        # as a config parameter later, I guess

        # TODO: this is rule R12
        self.flight_id: str = "-".join(
            [
                self.scheduled_departure.strftime("%d-%m-%Y"),
                self.orig,
                self.dest,
                self.flight_number,
                self.aircraft_registration,
            ]
        )

    @property
    def as_tuple(self) -> T.Tuple:
        return tuple(self.route)

    def __str__(self):
        return "-".join(self.route)


if __name__ == "__main__":

    g = AircraftGenerator(config=Config)
    g.populate()
    g.get_operational_interruptions()
    print("done")
