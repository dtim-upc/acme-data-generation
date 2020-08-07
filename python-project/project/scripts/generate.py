import datetime as dt
import logging
import random
import typing as T
from datetime import datetime
from pathlib import Path
from uuid import UUID
from collections import OrderedDict

from faker import Faker

from project.providers import fake
from project.base.config import BaseConfig
from project.models.data import amos, aims

config = BaseConfig()

Faker.seed(config.SEED)
random.seed(config.SEED)

logging.basicConfig(level=logging.DEBUG)  # use root logger


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

        size = self.config.SIZE
        self.slots = []
        self.flight_slots = []
        self.maintenance_slots = []

        for _ in range(size):

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
        for flight_slot in self.flight_slots:
            # produce a number of operational interruptions
            oi = fake.operational_interruption_event(
                max_id=self.config.SIZE, flight_slot=flight_slot
            )
            self.operational_interruptions.append(oi)
            self.maintenance_events.append(oi)

        for maintenance_slot in self.maintenance_slots:
            m = fake.maintenance_event(
                max_id=self.config.SIZE, maintenance_slot=maintenance_slot
            )

            self.maintenance_events.append(m)

        # create attachments
        self.attachments = []

        for oi in self.operational_interruptions:
            event_attachments = []
            for j in range(self.config.MAX_ATTCH_SIZE):
                fake_attachment = fake.attachment(operational_interruption=oi)
                event_attachments.append(fake_attachment)
            self.attachments.append(event_attachments)

        self.tlb_orders = [
            fake.technical_logbook_order(max_id=size)
            for _ in range(self.config.SIZE)
        ]

        self.forecasted_orders = [
            fake.forecasted_order(max_id=self.config.SIZE)
            for _ in range(self.config.SIZE)
        ]

        # https://stackoverflow.com/a/56735440/5819113
        self.workorders = [*self.tlb_orders, *self.forecasted_orders]

    @property
    def _status(self):
        return {
            k: len(v) for k, v in self.__dict__.items() if isinstance(v, list)
        }

    def __str__(self):
        return "\n".join([f"{k}: {v}" for k, v in self._status.items()])


if __name__ == "__main__":

    g = AircraftGenerator(config=config)
    # print(g.manufacturers)
    g.populate()
    print("Elements generated:")
    print(g)
    print("Done")
