import pytest
import typing as T

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from project.scripts.generate import AircraftGenerator


def test_instance_to_dict(fake):
    """tests that the as_dict method is working okay"""
    fs = fake.flight_slot(quality="good")
    fs.as_dict()