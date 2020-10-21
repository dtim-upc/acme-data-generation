from datetime import timedelta
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
    # test updated because of https://github.com/diegoquintanav/acme-data-generation/issues/2
    assert re_delaycode.search(bad_data.delaycode) is not None


def test_make_noisy(fake):
    "This test is very brittle. beware."

    re_noisy_string = re.compile(r"^\s*[a]{5}\s*$", flags=re.IGNORECASE)
    test_string = "aaaaa"
    noisified_string = fake.make_noisy(string=test_string)

    assert re_noisy_string.search(noisified_string) is not None


def test_flight_slots_diff_scheduled_arrival_departure(fake):
    """Tests that the difference between arrivals and departures is within range

    refer to the first part of the issue in
    https://github.com/diegoquintanav/acme-data-generation/issues/6
    """

    fs = fake.flight_slot()

    assert (fs.scheduledarrival - fs.scheduleddeparture) <= datetime.timedelta(days=1)


def test_flight_slots_diff_actual_arrival_departure(fake):
    """Tests that the difference between arrivals and departures is within range

    refer to the first part of the issue in
    https://github.com/diegoquintanav/acme-data-generation/issues/6
    """

    fs = fake.flight_slot()

    assert fs.actualarrival - fs.actualdeparture < datetime.timedelta(days=1)



def test_flight_slots_diff_arrivals(fake):
    """Tests that the difference between actual and scheduled arrivals makes sense
    """

    fs = fake.flight_slot()
    assert (fs.actualarrival >= fs.scheduledarrival)
    assert (fs.actualarrival - fs.scheduledarrival) <= timedelta(minutes=40)


def test_flight_slots_diff_departures(fake):
    """Tests that the difference between actual and scheduled departures makes sense
    """

    fs = fake.flight_slot()
    assert (fs.actualdeparture >= fs.scheduleddeparture)
    assert (fs.actualdeparture - fs.scheduleddeparture) <= timedelta(minutes=40)


def test_flight_slots_arrivals_on_cancellation(fake):
    """Test that flight slots marked as cancelled make sense

    this means they have no data in the fields actualarrival and actualdeparture
    """
    fs = fake.flight_slot(cancelled=True)

    assert fs.actualarrival is None
    assert fs.actualdeparture is None


def test_forecasted_orders_have_valid_executiondate(fake):

    fo = fake.forecasted_order()
    assert fo.executiondate <= fo.deadline
    assert fo.executiondate >= fo.planned

