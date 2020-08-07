import logging
import random
import typing as T
from tqdm import tqdm

from faker import Faker

from project.base.config import BaseConfig
from project.models.data import aims, amos
from project.providers import fake


class AircraftGenerator:
    def __init__(self, config):
        super().__init__()
        self.config = config

    def populate(self) -> "AircraftGenerator":

        # Creates a list of random Manufacturers
        # This is intended to be stored and used in aircraft-manufacturerinfo-lookup.csv
        self.manufacturers = [
            fake.manufacturer() for _ in range(self.config.FLEET_SIZE)
        ]

        # from these manufacturers, we obtain a list of aircraft_registration_codes
        # from which we obtain slots
        self.slots = []
        self.flight_slots = []
        self.maintenance_slots = []

        logging.info("Generating flight and maintenance slots")
        for _ in tqdm(range(self.config.SIZE)):

            # populate flight slots, maintenance slots, and slots
            if fake.boolean(self.config.PROB_FLIGHT_SLOT * 100):
                slot = fake.flight_slot(
                    manufacturer=fake.random_element(self.manufacturers)
                )
                self.flight_slots.append(slot)
            else:
                slot = fake.maintenance_slot(
                    manufacturer=fake.random_element(self.manufacturers)
                )
                self.maintenance_slots.append(slot)

            self.slots.append(slot)

        self.operational_interruptions = []
        self.maintenance_events = []

        # create_operational_interruptions:
        logging.info("Generating operational interruptions")
        for flight_slot in tqdm(self.flight_slots):
            # produce a number of operational interruptions
            oi = fake.operational_interruption_event(
                max_id=self.config.SIZE, flight_slot=flight_slot
            )
            self.operational_interruptions.append(oi)
            self.maintenance_events.append(oi)

        logging.info("Generating maintenance events")
        for maintenance_slot in tqdm(self.maintenance_slots):
            m = fake.maintenance_event(
                max_id=self.config.SIZE, maintenance_slot=maintenance_slot
            )
            self.maintenance_events.append(m)

        # create attachments
        self.attachments = []

        logging.info("Generating attachments")
        for oi in tqdm(self.operational_interruptions):
            event_attachments = []
            logging.debug(
                f"Generating attachments for oi '{oi.maintenanceid}'"
            )
            for j in range(self.config.MAX_ATTCH_SIZE):
                fake_attachment = fake.attachment(operational_interruption=oi)
                event_attachments.append(fake_attachment)
            self.attachments.append(event_attachments)

        logging.info(f"Generating technical logbook orders")
        self.tlb_orders = [
            fake.technical_logbook_order(max_id=self.config.SIZE)
            for _ in tqdm(range(self.config.SIZE))
        ]

        logging.info(f"Generating forecasted orders")
        self.forecasted_orders = [
            fake.forecasted_order(max_id=self.config.SIZE)
            for _ in tqdm(range(self.config.SIZE))
        ]

        logging.info(f"Generating work orders")
        # https://stackoverflow.com/a/56735440/5819113
        self.workorders = [*self.tlb_orders, *self.forecasted_orders]

        logging.info(f"Done")

    @property
    def status(self):
        return {
            k: len(v) for k, v in self.__dict__.items() if isinstance(v, list)
        }

    @property
    def total_generated(self):
        return sum(v for k, v in self.status.items())

    def __str__(self):
        return "\n".join([f"{k}: {v}" for k, v in self.status.items()])


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)  # use root logger
    config = BaseConfig(SIZE=10)
    Faker.seed(config.SEED)
    random.seed(config.SEED)
    # print(fake.manufacturer())

    g = AircraftGenerator(config=config)
    g.populate()
    logging.info("Elements generated:")
    logging.info(g)
    logging.info("Done")
