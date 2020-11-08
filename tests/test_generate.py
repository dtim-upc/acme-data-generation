import pytest
import typing as T
from statistics import mean
import re

from itertools import chain, permutations

from acme_data_generation.scripts.generate import AircraftGenerator
from acme_data_generation.base.config import BaseConfig


__doc__ = "Tests the generation of data"


def test_that_nothing_breaks(config):
    ag = AircraftGenerator(config=config)
    ag.populate()


@pytest.mark.parametrize("size", [10, 100])
def test_config_size(size, config):

    config.size = size
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert ag.config.size == config.size


@pytest.mark.parametrize("size", [10, 100])
def test_slots_size(config, size):

    config.flight_slots_size = size
    config.maintenance_slots_size = size
    total_size = size * 2

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.maintenance_slots) + len(ag.flight_slots) == total_size

    assert len(ag.maintenance_slots) == size
    assert len(ag.flight_slots) == size


@pytest.mark.parametrize("size", [10, 100])
def test_work_orders_size(size):
    """Tests that work orders' size matches

    :param config: [description]
    :type config: [type]
    :param size: [description]
    :type size: [type]
    """

    config = BaseConfig(size=size, forecasted_orders_size=size, tlb_orders_size=size)
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.tlb_orders) <= size
    assert len(ag.forecasted_orders) <= size
    assert len(ag.tlb_orders) + len(ag.forecasted_orders) == size


@pytest.mark.parametrize("attch_size", [1, 2])
@pytest.mark.parametrize("slots_size", [10, 100])
def test_attachments_size(slots_size, attch_size):

    config = BaseConfig(
        flight_slots_size=slots_size,
        maintenance_slots_size=slots_size,
        max_attach_size=attch_size,
    )
    ag = AircraftGenerator(config=config)
    assert ag.config.max_attach_size == attch_size
    assert ag.config.maintenance_slots_size == slots_size
    assert ag.config.flight_slots_size == slots_size

    ag.populate()

    # ois_events_size is controlled by flight_slots_size, not cancelled
    # maintenance_events_size is controlled by maintenance_slots_size
    assert sum(1 for f in ag.flight_slots if not f.cancelled) == len(
        ag.operational_interruptions
    )
    assert len(ag.maintenance_events) == len(ag.maintenance_slots)

    assert (
        len(ag.attachments)
        == (len(ag.maintenance_events) + len(ag.operational_interruptions))
        * ag.config.max_attach_size
    )


@pytest.mark.parametrize("custom_size", [10, 100])
def test_totals(custom_size):
    config = BaseConfig(
        size=custom_size,
        flight_slots_size=custom_size,
        maintenance_slots_size=custom_size,
        tlb_orders_size=custom_size,
        forecasted_orders_size=custom_size,
        max_attach_size=1,
        max_work_orders=1,
    )

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert config.size == custom_size
    assert config.flight_slots_size == custom_size
    assert config.maintenance_slots_size == custom_size
    assert config.tlb_orders_size == custom_size
    assert config.forecasted_orders_size == custom_size
    assert config.max_attach_size == 1
    assert config.max_work_orders == 1

    entities = [
        ag.flight_slots,
        ag.maintenance_slots,
        ag.maintenance_events,
        ag.operational_interruptions,
        ag.manufacturers,
        ag.work_packages,
        ag.tlb_orders,
        ag.forecasted_orders,
        ag.attachments,
        ag.maintenance_personnel,
    ]

    total_instances = sum([len(entity) for entity in entities])

    assert ag.total_entities == len(entities)
    assert ag.total_instances == total_instances


# -------------------------- test quality parameter -------------------------- #


@pytest.mark.parametrize("which", ["g", "b", "n"])
def test_quality_distributions_raises(which):

    prob_good=0.5
    prob_noisy=0.4
    prob_bad=0.1

    if which == "g":
        prob_good = 1
    elif which == "b":
        prob_bad = 1
    else:
        prob_noisy = 1

    with pytest.raises(AssertionError):
        BaseConfig(
            size=10,
            prob_good=prob_good,
            prob_noisy=prob_noisy,
            prob_bad=prob_bad,
        )


def test_quality_distributions_sums_to_1():

    config = BaseConfig(
        size=10,
        prob_good=0.5,
        prob_noisy=0.4,
        prob_bad=0.1,
    )

    assert config._prob_weights == [0.5, 0.4, 0.1]


def test_work_orders_have_valid_aircraftregistration(config):
    """Tests that the relation between workorders and maintenanceevents is meaningful

    Check issue #6

    Basically, we want to test that the following

    ```sql
    select
        *
    from
        "AMOS".workorders w
    where
        not exists (
        select
            *
        from
            "AMOS".maintenanceevents m2
        where
            w.aircraftregistration = m2.aircraftregistration
            and w.executiondate between starttime and starttime + duration)
    ```

    returns nothing, if prob_good = 1
    returns a proportion of size of prob_bad and prob_noisy, if they are not zero
    """

    config = BaseConfig(size=10)
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert ag.config._prob_weights == [1, 0, 0]

    # uno de los business rules dice que cada workorders por un aircraft debería
    # estar dentro de al menos un maintenance events
    # (w.executiondate between starttime and starttime+duration).
    airc_regs_wo = [
        wo.aircraftregistration for wo in chain(ag.forecasted_orders, ag.tlb_orders)
    ]

    airc_regs_me = [me.aircraftregistration for me in ag.maintenance_events]

    # Maintenance event can include several work orders and each work order is
    # inside one maintenance event. However, this reference is not explicit.
    # It is represented as I said above by the same aircraft registration and
    # the fact that the execution date of the work order is inside the time
    # interval of the maintenance event (startdate, startdate + duration).

    assert len(airc_regs_me) == len(airc_regs_wo)
    assert set(airc_regs_me) == set(airc_regs_wo)


def test_work_orders_have_valid_executiondate(config):
    """Tests that the relation between workorders and maintenanceevents is meaningful

    this covers the second part of the query


    Basically, we want to test that the following

    ```sql
    select
        *
    from
        "AMOS".workorders w
    where
        not exists (
        select
            *
        from
            "AMOS".maintenanceevents m2
        where
            w.aircraftregistration = m2.aircraftregistration
            and w.executiondate between starttime and starttime + duration)
    ```

    Check issue #6

    returns nothing, if prob_good = 1
    returns a proportion of size of prob_bad and prob_noisy, if they are not zero
    """

    config.size = 100
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert config._prob_weights == [1, 0, 0]

    wo_execution_date = [
        wo.executiondate for wo in chain(ag.tlb_orders, ag.forecasted_orders)
    ]

    me_airc_starttimes = [me.starttime for me in ag.maintenance_events]
    me_airc_endtimes = [me.starttime + me.duration for me in ag.maintenance_events]

    # Maintenance event can include several work orders and each work order is
    # inside one maintenance event. However, this reference is not explicit.
    # It is represented as I said above by the same aircraft registration
    # 2) and the fact that the execution date of the work order is inside the time
    # interval of the maintenance event (startdate, startdate + duration).

    for ed, start, end in zip(wo_execution_date, me_airc_starttimes, me_airc_endtimes):
        assert ed >= start
        assert ed <= end


def test_slots_with_same_aircraft_dont_overlap():
    """tests R20: Two Slots of the same aircraft cannot overlap in time.

    SELECT count(*)
    FROM flights f1
    WHERE NOT EXISTS
    (SELECT * FROM flights f2 WHERE f1.flightid <> f2.flightid and f1.aircraftregistration = f2.aircraftregistration
    and (f1.actualdeparture, f1.actualarrival) overlaps (f2.actualdeparture,f2.actualarrival));
    """

    config = BaseConfig(size=100)
    assert config._prob_weights == [1, 0, 0]
    ag = AircraftGenerator(config=config)
    ag.populate()

    # fetch all airc. regs.
    aircraft_registrations = [f.aircraftregistration for f in ag.flight_slots]

    # paranoid check
    assert ag.config.size == config.size
    assert len(ag.flight_slots) == config.size

    bad_checks_count = 0
    for ar in aircraft_registrations:
        # fetch all flights with that ar code
        same_aircraft_flights = [
            f
            for f in ag.flight_slots
            if (f.aircraftregistration == ar and f.cancelled is False)
        ]
        # check that the flights with this ar don't overlap
        if len(same_aircraft_flights) >= 2:
            for flight_1, flight_2 in permutations(same_aircraft_flights, 2):
                ts1 = flight_1.actualdeparture
                te1 = flight_1.actualarrival
                ts2 = flight_2.actualdeparture
                te2 = flight_2.actualarrival

                min_end = min(te1, te2)
                max_start = max(ts1, ts2)

                if min_end > max_start:
                    bad_checks_count += 1

    assert bad_checks_count == 0


def test_slots_with_same_aircraft_do_overlap():
    """tests R20: Two Slots of the same aircraft cannot overlap in time.

    SELECT count(*)
    FROM flights f1
    WHERE NOT EXISTS
    (SELECT * FROM flights f2 WHERE f1.flightid <> f2.flightid and f1.aircraftregistration = f2.aircraftregistration
    and (f1.actualdeparture, f1.actualarrival) overlaps (f2.actualdeparture,f2.actualarrival));
    """

    config = BaseConfig(size=100, prob_bad=1)
    assert config._prob_weights == [0, 0, 1]
    ag = AircraftGenerator(config=config)
    ag.populate()

    # fetch all airc. regs.
    aircraft_registrations = [f.aircraftregistration for f in ag.flight_slots]

    # paranoid check
    assert ag.config.size == config.size
    assert len(ag.flight_slots) == config.size

    bad_checks_count = 0
    for ar in aircraft_registrations:
        # fetch all flights with that ar code
        same_aircraft_flights = [
            f
            for f in ag.flight_slots
            if (f.aircraftregistration == ar and f.cancelled is False)
        ]
        # check that the flights with this ar don't overlap
        if len(same_aircraft_flights) >= 2:
            for flight_1, flight_2 in permutations(same_aircraft_flights, 2):
                ts1 = flight_1.actualdeparture
                te1 = flight_1.actualarrival
                ts2 = flight_2.actualdeparture
                te2 = flight_2.actualarrival

                min_end = min(te1, te2)
                max_start = max(ts1, ts2)

                if min_end > max_start:
                    bad_checks_count += 1

    assert bad_checks_count == 100