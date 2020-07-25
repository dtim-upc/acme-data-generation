import logging
import random
import typing as T
import datetime as dt
from pathlib import Path
from datetime import datetime
from uuid import UUID

from faker import Faker

from project.scripts.config import Config

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
        self.fleet: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.MSNs: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.models: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)
        self.manufacturers: T.List[str] = self._preallocate_array(size=self.config.FLEET_SIZE)

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

        self.scheduled_departures: T.List[datetime] = self._preallocate_array()
        self.scheduled_arrivals: T.List[datetime] = self._preallocate_array()
        self.actual_departures: T.List[datetime] = self._preallocate_array()
        self.actual_arrivals: T.List[datetime] = self._preallocate_array()
        self.delays: T.List[int] = self._preallocate_array()
        self.cancelled: T.List[bool] = self._preallocate_array()
        self.delay_codes: T.List[str] = self._preallocate_array()

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

            if self.cancelled[i]:
                self.delays[i] = 0
                self.delay_codes[i] = None
                self.actual_arrivals[i] = None
                self.actual_departures[i] = None
            else:  # if flight was not self.cancelled, then set self.delays, if any
                # define a random delay in minutes
                self.delays[i]: int = random.randrange(0, self.config.MAX_DELAY)

                # if delay ocurred, determine reason
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

    def rest(self):
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
        self.maintenance_id: T.List[int] = self._preallocate_array()
        self.airport_maintenance: T.List[str] = self._preallocate_array()
        self.subsystem: T.List[str] = self._preallocate_array()
        self.starttimes: T.List[datetime] = self._preallocate_array()

        # AMOS.maintenanceevents.interval
        self.days: T.List[int] = self._preallocate_array()
        self.hours: T.List[int] = self._preallocate_array()
        self.minutes: T.List[int] = self._preallocate_array()

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

        # populate data
        for i in range(self.config.SIZE):
            # pick a slotkind at random from "flight, maintenance"
            self.slots_kinds[i] = random.choice(self.config.SLOTKINDOPTIONS)

            # if slot kind is Maintenance, or if that flight presented delays, specify details
            # check
            if self.slots_kinds[i] == "Maintenance" or self.delays[i] > 0:
                self.programmed[i] = fake.pybool()  # AIMS.maintenance.programmed
                self.maintenance_id[i] = random.randrange(self.config.SIZE)  # AMOS.maintenanceevents.maintenanceid
                # TODO: why 250? should this be a parameter
                self.airport_maintenance[i] = random.choice(self.config.AIRPORTCODES)  #  AMOS.maintenanceevents.airport
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

                # TODO: check why is this
                self.departure[i] = self.scheduled_departures[i]  # I think this is AMOS.maintenanceevents.departure

                # AMOS.attachments
                for j in range(self.config.MAX_ATTCH_SIZE):
                    self.attachment_files[i][j] = fake.uuid4()
                    self.attachment_events[i][j] = str(self.maintenance_id[i])

                # AMOS.workpackages
                self.work_package_ids[i] = random.randrange(self.config.SIZE)  # AMOS.workpackages.workpackageid
                self.execution_dates[i] = self.departure[i]  # AMOS.workpackages.executiondate
                self.execution_places[i] = self.airport_maintenance[i]  # AMOS.workpackages.executionplace

                #
                for j in range(self.config.MAX_WORK_ORDERS):
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
                    self.workorder_mels[i][j] = random.choice(self.config.MELCATHEGORYOPTIONS)

                    _mel_mapping = {
                        "A": dt.timedelta(days=-3),
                        "B": dt.timedelta(days=-10),
                        "C": dt.timedelta(days=-30),
                        "D": dt.timedelta(days=-120),
                    }

                    self.workorder_reportingdate[i][j] = self.workorder_duedates[i][j] + _mel_mapping.get(
                        self.workorder_mels[i][j], dt.timedelta(days=-5)
                    )

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

    #                 /////////////////////////
    #                 //if flight
    #                 //if (!slotKinds[i].equalsIgnoreCase("Flight")) continue;

    #                 String origin = airportCodes[r.nextInt(airportCodes.length)];
    #                 String dest = airportCodes[r.nextInt(airportCodes.length)];
    #                 while (origin.equalsIgnoreCase(dest)) {
    #                     dest = airportCodes[r.nextInt(airportCodes.length)];
    #                 }
    #                 originDest[i] = new Pair(origin, dest);
    #                 if (!orgDestToFlightNo.containsKey(origin + "-" + dest)) {
    #                     String flightNo = digits.charAt(r.nextInt(10)) + "" + digits.charAt(r.nextInt(10)) + digits.charAt(r.nextInt(10)) + digits.charAt(r.nextInt(10));
    #                     orgDestToFlightNo.put(origin + "-" + dest, flightNo);
    #                 }

    #                 passengers[i] = r.nextInt((MAX_PAS - MIN_PAS) + 1) + MIN_PAS;
    #                 cabinCrew[i] = r.nextInt((MAX_CCREW - MIN_CCREW) + 1) + MIN_CCREW;
    #                 flightCrew[i] = r.nextInt((MAX_FCREW - MIN_FCREW) + 1) + MIN_FCREW;

    #                 String day = (scheduledDepartures[i].getDate() < 10) ? "0" + scheduledDepartures[i].getDate() : "" + scheduledDepartures[i].getDate();
    #                 String month = (1 + scheduledDepartures[i].getMonth() < 10) ? "0" + (1 + scheduledDepartures[i].getMonth()) : "" + (1 + scheduledDepartures[i].getMonth());
    #                 String year = ((1900 + scheduledDepartures[i].getYear()) + "").substring(2, 4);

    #                 //System.out.println("timestamp: "+scheduledDepartures[i]);
    #                 //System.out.println("date1: "+scheduledDepartures[i].getDate()+" "+scheduledDepartures[i].getMonth()+" "+scheduledDepartures[i].getYear());
    #                 //System.out.println("date2: "+day+" "+month+" "+year);

    #                 flightIDs[i] = day + month + year + "-" + originDest[i].first + "-" + originDest[i].second + "-" + orgDestToFlightNo.get(originDest[i].toString()) + "-" + aircraftRegs[i];
    #                 //flightIDs[i] =  scheduledDepartures[i] + "-" + originDest[i].first + "-" + originDest[i].second + "-" + orgDestToFlightNo.get(originDest[i].toString()) + "-" + aircraftRegs[i];

    #             }

    def populate(self):
        self.create_fleet()
        self.create_aircraft_registrations()
        self.create_timestamps()
        self.rest()
        return self

    def get_flights(self, output: Path = None) -> T.Generator:
        output_flights = (
            [
                self.aircraft_registrations[i],
                self.scheduled_departures[i],
                self.scheduled_arrivals[i],
                self.slots_kinds[i],
                self.flight_ids[i],
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
    def as_tuple(self) -> tuple:
        return tuple(self.route)

    def __str__(self):
        return "-".join(self.route)


if __name__ == "__main__":

    g = AircraftGenerator(config=Config)
    g.populate()
    logging.debug(g.flight_ids)

