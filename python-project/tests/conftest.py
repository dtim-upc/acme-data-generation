import typing as T
from datetime import datetime

import pytest
from faker import Faker

from project.base.config import BaseConfig
from project.providers import AirportProvider
from project.scripts.generate import AircraftGenerator


@pytest.fixture()
def config():
    config = BaseConfig(
        seed=42,
        size=10,  # number of rows of the CSV
        max_attch_size=1,
        max_work_orders=1,
    )

    yield config


@pytest.fixture()
def fake():
    fake = Faker()
    Faker.seed(42)
    fake.add_provider(AirportProvider)
    yield fake


@pytest.fixture()
def gen(config):
    ag = AircraftGenerator(config=config)
    ag.populate()
    yield ag
