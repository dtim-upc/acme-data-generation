import pytest
import typing as T
from project.scripts.generate import AircraftGenerator

__doc__ = "tests that the populate produces stable results"


@pytest.mark.parametrize("size", [10, 100, 1000, 10000])
def test_config_size(size, config):

    config.SIZE = size
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert ag.config.SIZE == config.SIZE


@pytest.mark.parametrize("size", [10, 100, 1000, 10000])
def test_size_populated(config, size):

    config.SIZE = size
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.flight_ids) == config.SIZE
    assert len(ag.aircraft_registrations) == config.SIZE


@pytest.mark.parametrize("size", [10, 100, 1000, 10000])
def test_get_flights(config, size):

    config.SIZE = size
    ag = AircraftGenerator(config=config)
    ag.populate()

    flights_gen = ag.get_flights()

    assert isinstance(flights_gen, T.Generator)
    assert sum(1 for _ in ag.get_flights()) == config.SIZE

