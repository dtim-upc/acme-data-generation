import datetime as dt
import logging
import random
import typing as T
from datetime import datetime
from pathlib import Path
from uuid import UUID

from faker import Faker

from project.providers import fake
from project.scripts.config import Config

Faker.seed(Config.SEED)
random.seed(Config.SEED)

logging.basicConfig(level=logging.DEBUG)  # use root logger


class AircraftGenerator:
    def __init__(self, config):
        super().__init__()
        self.config = Config()

    def create_manufacturers(self) -> "AircraftGenerator":
        """Creates a list of random Manufacturers 
        
        This is intended to be stored and used in aircraft-manufacturerinfo-lookup.csv

        :return: A list of configurable size
        :rtype: T.Tuple
        """
        self.manufacturers = [
            fake.manufacturer() for _ in range(self.config.FLEET_SIZE)
        ]
        return self

    def create_reporters(self):
        pass

    def create_flight_slots(self):
        self.slots = [
            fake.any_slot(prob_flight_slot=self.config.PROB_FLIGHT_SLOT)
            for _ in range(self.config.SIZE)
        ]
        return self

    def create_operation_interruptions(self):
        self.ois = [
            fake.operational_interruption_event()
            for _ in range(self.config.SIZE)
        ]
        return self

    def create_attachments(self):

        if not getattr(self, "ois", False):
            self.create_operation_interruptions()

        # AMOS.attachments
        # A maintenance event can have more than one attachment. This is controlled by MAX_ATTCH_SIZE
        attachments = []

        for oi in self.ois:
            for j in range(self.config.MAX_ATTCH_SIZE):
                event_attachments = []
                fake_attachment = fake.attachment()
                # TODO: this is rule R5:
                # event of an Attachement is a reference to maintenanceID of MaintenanceEvents
                fake_attachment.event = oi.maintenanceid
                event_attachments.append(fake_attachment)
            attachments.append(event_attachments)

        self.attachments = attachments
        return self

    def create_tlb_orders(self):
        return [
            fake.technical_logbook_order(max_id=self.config.SIZE)
            for _ in range(self.config.SIZE)
        ]

    def create_forecasted_orders(self):
        return [
            fake.forecasted_order(max_id=self.config.SIZE)
            for _ in range(self.config.SIZE)
        ]

    def populate(self):
        self.create_manufacturers()
        self.create_reporters()
        self.create_flight_slots()
        self.create_operation_interruptions()
        self.create_attachments()
        self.create_tlb_orders()
        self.create_forecasted_orders()

if __name__ == "__main__":

    g = AircraftGenerator(config=Config)
    # print(g.manufacturers)
    g.populate()
