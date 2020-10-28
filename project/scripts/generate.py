import csv
import logging
import random
import typing as T
from datetime import timedelta
from itertools import chain
from pathlib import Path

from faker import Faker
from project.base.config import BaseConfig
from project.models.data.serializable import Manufacturer, Reporter
from project.models.declarative import aims, amos
from project.providers.airport import fake_airport
from project.scripts.db_utils import get_session
from sqlalchemy import create_engine
from tqdm import tqdm


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
            writer = csv.DictWriter(
                file.open("wt"),
                fieldnames=entities[0].as_dict().keys(),
                delimiter=",",
            )

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

        # Creates a list of random Manufacturers
        # This is intended to be stored and used 
        # in aircraft-manufacturerinfo-lookup.csv

        # -------------------------- aircraft manufacturers ------------------ #

        self.manufacturers = [
            fake_airport.manufacturer(
                fake_airport.quality(self.config._prob_weights))
                for _ in range(self.config.fleet_size)
        ]

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
        for flight_slot in tqdm(self.flight_slots):
            # R13: If flight slot has some delay, that introduces 
            # an operational interruption of some kind
            if flight_slot.delaycode is not None:
                operational_interruption = fake_airport.operational_interruption_event(
                    max_id=self.config.size,
                    slot=flight_slot,
                    quality=fake_airport.quality(self.config._prob_weights),
                )
                self.operational_interruptions.append(operational_interruption)

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

        for work_order in tqdm(chain(self.forecasted_orders, self.tlb_orders)):
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

        logging.info("Generating attachments")

        for event in tqdm(chain(self.operational_interruptions, self.maintenance_events)):
            event_attachments = []
            # R5
            logging.debug(f"Generating attachments for event '{event.maintenanceid}'")
            for j in range(random.randint(a=1, b=self.config.max_attach_size)):
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
