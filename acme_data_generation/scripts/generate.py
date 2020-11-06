import csv
import logging
import random
import typing as T
from datetime import datetime, timedelta
from itertools import chain, zip_longest
from pathlib import Path

from faker import Faker
from acme_data_generation.base.config import BaseConfig
from acme_data_generation.models.data.serializable import Manufacturer, Reporter
from acme_data_generation.models.declarative import aims, amos
from acme_data_generation.providers.airport import fake_airport
from acme_data_generation.scripts.db_utils import get_session
from sqlalchemy import create_engine
from tqdm import tqdm



def grouper(iterable, n, fillvalue=None):
    # https://stackoverflow.com/a/434411/5819113
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class AircraftGenerator:
    def __init__(self, config):
        super().__init__()
        self.config = config

    def to_csv(self, path: Path) -> Path:

        # create path if not exists
        path.mkdir(exist_ok=True)

        logging.info("Writing instances to CSV files")
        for tablename, entities in tqdm(self.state.items(), unit="file"):
            file = path.joinpath(f"{tablename}.csv")

            # creates a dictwriter
            # in windows, dictwriter adds a newline at the end of each row
            # https://stackoverflow.com/a/3191811/5819113
            writer = csv.DictWriter(
                file.open("wt", newline=''),
                fieldnames=entities[0].as_dict().keys(),
                delimiter=",")

            writer.writeheader()

            for entity in entities:
                writer.writerow(entity.as_dict())

        logging.info("Done")
        return path

    def to_sql(self, session, db_url: T.Optional[str] = None):

        logging.info("Inserting instances to DB tables")
        for k, v in tqdm(self.state.items(), unit="table"):
            for instance in v:
                # if it has a _mapper_ attribute then it is a sqlalchemy mapped class
                if getattr(instance, "__mapper__", False):
                    session.add(instance)
        session.commit()
        logging.info("Done")

    def populate(self) -> "AircraftGenerator":

        # --------------------------- maintenance personnel -------------------#

        logging.info("Generating maintenance personnel list")

        self.maintenance_personnel = []

        for _ in tqdm(range(self.config.personnel_list_size)):
            self.maintenance_personnel.append(
                fake_airport.reporter(
                    quality=fake_airport.quality(self.config._prob_weights)))

        # -------------------------- aircraft manufacturers ------------------ #

        # Creates a list of random Manufacturers
        # This is intended to be stored and used 
        # in aircraft-manufacturerinfo-lookup.csv
        logging.info("Generating aircraft fleet")

        self.manufacturers = []
        for _ in tqdm(range(self.config.fleet_size)):
            self.manufacturers.append(
                fake_airport.manufacturer(
                    quality=fake_airport.quality(self.config._prob_weights)))

        # from these manufacturers, we obtain a list of aircraft_registration_codes
        # from which we obtain slots

        self.flight_slots = []
        self.maintenance_slots = []

        # ------------------------------- flight slots ----------------------- #

        logging.info("Generating flight slots")

        for _ in tqdm(range(self.config.flight_slots_size)):
            flight_slot = fake_airport.flight_slot(
                manufacturer=fake_airport.random_element(self.manufacturers),
                quality=fake_airport.quality(self.config._prob_weights),
            )
            self.flight_slots.append(flight_slot)

        # R20
        # verify overlaps if any, and fix them with prob_good probability

        # sort flights per scheduleddeparture, in-place
        # flight slots that were cancelled are considered as of higher value
        # in the sort. In other words, they will end up in the end of the list.
        # this is arbitrary.
        self.flight_slots.sort(
            key=lambda flight: flight.actualdeparture or datetime.max)

        # fetch the indexes of those flights that were not cancelled
        # we need those to not overlap
        non_cancelled_flights_indexes = [
            idx for idx, f in enumerate(self.flight_slots)
            if not f.cancelled]

        for flight1_idx, flight2_idx in grouper(non_cancelled_flights_indexes, n=2, fillvalue=None):
            # assuming list is sorted, we
            # compare flights in chunks of two. An overlap looks like
            #
            # ---|--------|---------|--------|------> time
            #   ts1      ts2       te1      te2
            #
            # where ts = time start, te = time end. We want to fix this,
            # by swapping ts2 with te1
            #
            # ---|--------|---------|--------|------> time
            #   ts1      te1       ts2 +    te2
            #                  random interval      
            
            if flight2_idx is None:
                # we may have an odd number of flights to fix. If that's the case
                # the last index will be None, and we know this flight needs no
                # correction
                continue
            
            ts1 = self.flight_slots[flight1_idx].actualdeparture
            te1 = self.flight_slots[flight1_idx].actualarrival
            ts2 = self.flight_slots[flight2_idx].actualdeparture
            te2 = self.flight_slots[flight2_idx].actualarrival

            # get both ends of the eventual overlap
            # will get te1 if flight is not overlapping
            min_end = min(te1, te2)
            # will get ts2 if flight is not overlapping
            max_start = max(ts1, ts2)

            # means we have an overlap guys, put your gear on
            if min_end > max_start:
                # swap start of f2 with end of f1
                # by reassigning dates to flights

                # make the start of flight 2 something between the ending
                # of flight 1 and the ending of flight 2
                self.flight_slots[flight2_idx].actualdeparture = te1

                # make the start of ending of flight 1, the beginning of flight 2
                self.flight_slots[flight1_idx].actualarrival = ts2

        # ----------------------------- maintenance slots -------------------- #

        logging.info("Generating maintenance slots")
        for _ in tqdm(range(self.config.maintenance_slots_size)):
            maintenance_slot = fake_airport.maintenance_slot(
                manufacturer=fake_airport.random_element(self.manufacturers),
                quality=fake_airport.quality(self.config._prob_weights),
            )
            self.maintenance_slots.append(maintenance_slot)

        # ------------------------- operational interruptions ---------------- #

        # from the existing slots, create an operational interruption
        # if flight slot, produces an operational interruption
        # if maintenance slot, produces a maintenance slot
        self.operational_interruptions = []
        self.maintenance_events = []

        logging.info("Generating operational interruptions")

        for flight_slot in self.flight_slots:
            # R13: If flight slot has some delay, that introduces 
            # an operational interruption of some kind
            if flight_slot.delaycode is not None:
                operational_interruption = fake_airport.operational_interruption_event(
                    max_id=self.config.size,
                    slot=flight_slot,
                    quality=fake_airport.quality(self.config._prob_weights),
                )
                self.operational_interruptions.append(operational_interruption)
        
        for _ in tqdm(self.operational_interruptions):
            pass # hacky way to display a bar
        
        logging.info("Generating maintenance events")

        for maintenance_slot in tqdm(self.maintenance_slots):
            # maintenance slots produce only maintenance events
            # flight slots produce operational interruptions
            
            maintenance_event = fake_airport.maintenance_event(
                max_id=self.config.size,
                slot=maintenance_slot,
                quality=fake_airport.quality(self.config._prob_weights),
            )

            # R14
            if maintenance_event.kind == "Revision":
                # split duration in number of days
                assert maintenance_event.duration.days >= 1
                # add an extra day if there is a non integer number of days
                extra_day = (1 if bool(maintenance_event.duration.total_seconds() % (24*60*60)) else 0)
                _splitted_maintenance_events = [maintenance_event] * (maintenance_event.duration.days + extra_day)

                for event_chunk in _splitted_maintenance_events:
                    event_chunk.duration = timedelta(days=1)
                    self.maintenance_events.append(event_chunk)
            else:
                self.maintenance_events.append(maintenance_event)

        # ---------------------------------------------------------------------------- #
        #                                  work orders                                 #
        # ---------------------------------------------------------------------------- #

        self.forecasted_orders = []
        self.tlb_orders = []

        # ----------------  technical logbook orders ----------------------- #

        # We produce a number of work orders equal to maintenance events
        # and we sample the type using probabilities

        proba_fo = self.config.proba_forecast_order
        
        logging.info(
            "Generating work orders"
        )

        # only maintenance events produce work orders, operationalinterruptions don't
        for maintenance_event in tqdm(self.maintenance_events):
            
            order_kind = ("Forecast" if random.random() < proba_fo else "TechnicalLogBook")

            order = fake_airport.work_order(
                max_id=len(self.maintenance_events),
                quality=fake_airport.quality(self.config._prob_weights),
                maintenance_event=maintenance_event,
                kind=order_kind
            )

            if order_kind == "Forecast":
                self.forecasted_orders.append(order)
            else:
                self.tlb_orders.append(order)

        # ------------------------------- work packages ------------------------------ #

        logging.info("Generating work packages")
        self.work_packages = []

        tqdm_total_wp = len(self.forecasted_orders) + len(self.tlb_orders)

        for work_order in tqdm(chain(self.forecasted_orders, self.tlb_orders), total=tqdm_total_wp):
            # R30: each work order produces a number of workpackages less or equal than 
            # config.max_work_packages
            work_packages = []
            for _ in range(random.randint(a=1, b=self.config.max_work_packages)):
                work_package = fake_airport.work_package(
                    quality=fake_airport.quality(self.config._prob_weights),
                    max_id=self.config.size,
                    work_order = work_order)
                work_packages.append(work_package)
                
            self.work_packages.extend(work_packages)

        # ---------------------------- create attachments -------------------- #

        self.attachments = []
        # since ois inherits from maintenance events,
        # ois are also maintenance events
        tqdm_total_at = len(self.operational_interruptions) + len(self.maintenance_events)

        logging.info("Generating attachments")

        for event in tqdm(chain(self.operational_interruptions, self.maintenance_events), total=tqdm_total_at):
            event_attachments = []
            # R5
            logging.debug(f"Generating attachments for event '{event.maintenanceid}'")
            for _ in range(random.randint(a=1, b=self.config.max_attach_size)):
                fake_attachment = fake_airport.attachment(event=event)
                event_attachments.append(fake_attachment)

            # we don't want nested lists
            self.attachments.extend(event_attachments)


        logging.info("Done")
        return self

    @property
    def state(self):
        return {k: v for k, v in self.__dict__.items() if isinstance(v, list)}

    @property
    def total_instances(self):
        return sum(len(v) for k, v in self.state.items())

    @property
    def total_entities(self):
        return sum(1 for _ in self.state.keys())

    def __str__(self):
        return "\n".join([f"{k}: {len(v)}" for k, v in self.state.items()])
