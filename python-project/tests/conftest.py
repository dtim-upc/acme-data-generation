import pytest
from faker import Faker
from project.providers import AirportProvider
from project.base.config import BaseConfig

from datetime import datetime
import typing as T


@pytest.fixture()
def config():
    class TestConfig(BaseConfig):

        SEED: int = 42
        SIZE: int = 10  # number of rows of the CSV
        MAX_ATTCH_SIZE: int = 1
        MAX_WORK_ORDERS: int = 1

    yield TestConfig()


@pytest.fixture()
def fake():
    fake = Faker()
    Faker.seed(42)
    fake.add_provider(AirportProvider)
    yield fake
