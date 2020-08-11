import typing as T
from datetime import datetime

import pytest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from project.base.config import BaseConfig
from project.providers import AirportProvider
from project.scripts.generate import AircraftGenerator
from project.scripts.db_utils import create_all, delete_all


@pytest.fixture()
def config():
    config = BaseConfig(
        seed=42,
        size=10,  # number of rows of the CSV
        max_attch_size=1,
        max_work_orders=1,
        db_url="postgresql://postgres:admin@localhost:54320/testdb",
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


@pytest.fixture()
def session(config):

    engine = create_engine(config.db_url)

    if not database_exists(engine.url):
        create_database(engine.url)

    create_all(engine)

    # create a configured "Session" class
    a_session = sessionmaker(bind=engine)

    # create a Session
    session = a_session()

    yield session

    # teardown database
    session.close()
    delete_all(engine)

    if database_exists(engine.url):
        drop_database(engine.url)

    engine.dispose()
