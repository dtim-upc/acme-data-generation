import csv
import logging
import random
import typing as T
from itertools import chain
from pathlib import Path

from faker import Faker
from sqlalchemy import create_engine
from tqdm import tqdm

from project.base.config import BaseConfig
from project.models.declarative import aims, amos
from project.models.data.serializable import Manufacturer, Reporter
from project.providers import fake
from project.scripts.db_utils import get_session


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
        # This is intended to be stored and used in aircraft-manufacturerinfo-lookup.csv

        # -------------------------- aircraft manufacturers ------------------ #

        self.manufacturers = [
            fake.manufacturer() for _ in range(self.config.fleet_size)
        ]

        # from these manufacturers, we obtain a list of aircraft_registration_codes
        # from which we obtain slots

        self.slots = []
        self.flight_slots = []
        self.maintenance_slots = []

        # ------------------------------- flight slots ----------------------- #

        logging.info("Generating flight slots")
        for _ in tqdm(range(self.config.flight_slots_size)):
            slot = fake.flight_slot(
                manufacturer=fake.random_element(self.manufacturers),
                quality=fake.random_quality(self.config._prob_weights),
            )
            self.flight_slots.append(slot)

        # ----------------------------- maintenance slots -------------------- #

        logging.info("Generating maintenance slots")
        for _ in tqdm(range(self.config.maintenance_slots_size)):
            slot = fake.maintenance_slot(
                manufacturer=fake.random_element(self.manufacturers),
                quality=fake.random_quality(self.config._prob_weights),
            )
            self.maintenance_slots.append(slot)

        # ----------------------------- all slots ---------------------------- #

        logging.info("Generating slots")
        # https://stackoverflow.com/a/56735440/5819113
        self.slots = [
            aims.Slot.from_child(obj)
            for obj in tqdm(chain(self.flight_slots, self.maintenance_slots))
        ]

        # ------------------------- operational interruptions ---------------- #

        self.operational_interruptions = []
        self.maintenance_events = []

        # from the existing flight slots, create an operational interruption and
        # a maintenance event

        logging.info("Generating operational interruptions")
        for flight_slot in tqdm(self.flight_slots):
            # produce a number of operational interruptions
            oi = fake.operational_interruption_event(
                max_id=self.config.size,
                flight_slot=flight_slot,
                quality=fake.random_quality(self.config._prob_weights),
            )

            self.operational_interruptions.append(oi)
            self.maintenance_events.append(amos.MaintenanceEvent.from_child(oi))

        # ---------------------------- maintenance events -------------------- #

        # from each of the existing maintenance slots, create a maintenance event

        logging.info("Generating maintenance events")

        for maintenance_slot in tqdm(self.maintenance_slots):
            m = fake.maintenance_event(
                max_id=self.config.size,
                maintenance_slot=maintenance_slot,
                quality=fake.random_quality(self.config._prob_weights),
            )
            self.maintenance_events.append(m)

        # ---------------------------- create attachments -------------------- #

        self.attachments = []

        logging.info("Generating attachments")
        for oi in tqdm(self.operational_interruptions):
            event_attachments = []
            logging.debug(f"Generating attachments for oi '{oi.maintenanceid}'")
            for j in range(self.config.max_attch_size):
                fake_attachment = fake.attachment(operational_interruption=oi)
                event_attachments.append(fake_attachment)

            # we don't want nested lists
            self.attachments.extend(event_attachments)

        # ------------------------------- work packages ------------------------------ #

        logging.info("Generating work packages")
        self.work_packages = []

        # for every maintenance event, we create a work package
        for maintenance_event in tqdm(self.maintenance_events):
            work_package = fake.work_package(
                quality=fake.random_quality(self.config._prob_weights),
                max_id=self.config.size,
                maintenance_event=maintenance_event,
            )
            self.work_packages.append(work_package)

        # ---------------- work orders from tlb and forecasted orders -------- #

        # every work package is linked to at least one work order
        # that is, each one of tlb and forecast orders must be linked to a workpackage
        self.forecasted_orders = []
        self.work_orders = []
        self.tlb_orders = []

        logging.info(
            "Generating technical logbook orders and their work order relatives"
        )

        # so we want to produce a number of tlb and forecasted orders that add up to the number
        # of work orders which is the same number as work packages
        # we will do it 50%/50% approx

        _tlb_wp_size_end = round(len(self.work_packages) * 0.5)
        _forecast_wp_start = len(self.work_packages) - _tlb_wp_size_end

        for tlb_work_package in tqdm(self.work_packages[:_tlb_wp_size_end]):
            fake_tlb = fake.technical_logbook_order(
                max_id=self.config.maintenance_events_size,
                quality=fake.random_quality(self.config._prob_weights),
                work_package=tlb_work_package,
            )

            self.tlb_orders.append(fake_tlb)
            self.work_orders.append(amos.WorkOrder.from_child(fake_tlb))

        # ----------------------------- forecasted orders -------------------- #

        logging.info("Generating forecasted orders and their work_orders relatives")
        for fo_work_package in tqdm(self.work_packages[_forecast_wp_start:]):
            fake_fo = fake.forecasted_order(
                max_id=self.config.maintenance_slots_size,
                quality=fake.random_quality(self.config._prob_weights),
                work_package=fo_work_package,
            )

            self.forecasted_orders.append(fake_fo)
            self.work_orders.append(amos.WorkOrder.from_child(fake_fo))

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
