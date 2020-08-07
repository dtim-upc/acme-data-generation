import pytest
import typing as T
import datetime
import re

"""Tests that the airport random generator behaves according to some rules"""

re_aircraftregistration = re.compile(r"XY-[A-Z]{3}")
re_flightid = re.compile(r"\d{2}-\d{2}-\d{4}-[A-Z]{3}-[A-Z]{3}-\d{4}-XY-[A-Z]{3}")
re_airport = re.compile(r"[A-Z]{3}")
re_delaycode = re.compile(r"\d{2}")


def test_maintenance_slot(fake):

    data = fake.maintenance_slot()

    assert re_aircraftregistration.search(data.aircraftregistration)
    assert data.scheduleddeparture < data.scheduledarrival
    assert data.kind == "Maintenance"
    assert isinstance(data.programmed, bool)


def test_flight_slot(fake, config):

    data = fake.flight_slot()

    assert re_aircraftregistration.search(data.aircraftregistration)
    assert data.scheduleddeparture < data.scheduledarrival
    assert data.kind == "Flight"
    assert re_airport.search(data.departureairport)
    assert re_airport.search(data.arrivalairport)
    assert isinstance(data.cancelled, bool)
    assert re_flightid.search(data.flightid)
    assert config.MIN_PAS <= data.passengers <= config.MAX_PAS
    assert config.MIN_CCREW <= data.cabincrew <= config.MAX_CCREW
    assert config.MIN_FCREW <= data.flightcrew <= config.MAX_FCREW


def test_cancelled_flight(fake, config):
    data = fake.flight_slot(cancelled=True)

    assert data.scheduleddeparture < data.scheduledarrival
    assert data.actualdeparture is None
    assert data.actualarrival is None
    assert data.delaycode is None


def test_non_cancelled_flight(fake, config):
    data = fake.flight_slot(cancelled=False)
    assert data.actualdeparture < data.actualarrival
    assert re_delaycode.search(data.delaycode)

