import pytest
import typing as T
import datetime
import re

"""Tests that the airport random generator behaves according to some rules"""

re_aircraftregistration = re.compile(r"^XY-[A-Z]{3}$")
re_flightid = re.compile(r"^\d{6}-[A-Z]{3}-[A-Z]{3}-\d{4}-XY-[A-Z]{3}$")
re_airport = re.compile(r"^[A-Z]{3}$")
re_delaycode = re.compile(r"^\d{2}$")


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
    assert config.min_pas <= data.passengers <= config.max_pas
    assert config.min_ccrew <= data.cabincrew <= config.max_ccrew
    assert config.min_fcrew <= data.flightcrew <= config.max_fcrew


def test_cancelled_flight(fake, config):
    data = fake.flight_slot(cancelled=True)

    assert data.scheduleddeparture < data.scheduledarrival
    assert data.actualdeparture is None
    assert data.actualarrival is None
    assert data.delaycode is None


# -------------------------------- test rules -------------------------------- #


def test_rule_R22_good(fake, config):

    data = fake.flight_slot(cancelled=False)

    assert data.actualdeparture < data.actualarrival
    assert re_delaycode.search(data.delaycode)
    
    data = fake.flight_slot(cancelled=True)

    # if flight is cancelled, then some attributes must be empty
    assert data.delaycode is None
    assert data.actualarrival is None
    assert data.actualdeparture is None

def test_rule_R22_bad(fake, config):

    bad_data = fake.flight_slot(quality="bad", cancelled=False)

    assert bad_data.actualdeparture > bad_data.actualarrival
    assert re_delaycode.search(bad_data.delaycode) is None





def test_bad_quality(fake):
    """This tests rule R22"""
    assert data.actualdeparture > data.actualarrival
    assert re_delaycode.search(data.delaycode)


@pytest.mark.skip("not implemented")
def test_noisy_quality(config):
    assert False


@pytest.mark.skip("not implemented")
def test_good_quality(config):
    assert False
