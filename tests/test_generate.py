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


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_config_size(size, config):

    config.size = size
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert ag.config.size == config.size


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_slots_size(config, size):

    config.flight_slots_size = size
    config.maintenance_slots_size = size
    total_size = size * 2

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.maintenance_slots) + len(ag.flight_slots) == total_size

    assert len(ag.maintenance_slots) == size
    assert len(ag.flight_slots) == size


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_work_orders_size(config, size):

    # work orders should be the size of work packages
    # work packages are the size of maintenance_events
    # and maintenance_events are the size of operational interruptions + common maintenance events
    # operational interruptions are the size of flight slots
    # common maintenance events are the size of maintenance slots
    # config.tlb_orders_size = size
    # config.forecasted_orders_size = size

    # since flight slots = size, and maintenance slots = size
    # work orders should be 2 * size,
    # and tlb_orders and forecasted orders are split 50/50 of that

    config.size = size
    config.forecasted_orders_size = size
    config.tlb_orders_size = size

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.tlb_orders) == size
    assert len(ag.forecasted_orders) == size
    assert len(ag.tlb_orders) + len(ag.forecasted_orders) == size * 2


@pytest.mark.parametrize("attch_size", [1, 2])
@pytest.mark.parametrize("oi_size", [10, 100, 1000])
def test_attachments_size(config, oi_size, attch_size):

    # ois_size is controlled by flight_slots_size
    # maintenance_events_size is controlled by maintenance_slots_size

    config.flight_slots_size = oi_size
    config.max_attach_size = attch_size

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.attachments) == oi_size * attch_size


@pytest.mark.parametrize("custom_size", [10, 100, 1000])
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

    entities =  [
        ag.flight_slots,
        ag.maintenance_slots,
        ag.maintenance_events,
        ag.operational_interruptions,
        ag.manufacturers,
        ag.work_packages,
        ag.tlb_orders,
        ag.forecasted_orders,
        ag.attachments,
        ag.maintenance_personnel
        ]

    total_instances = sum([len(entity) for entity in entities])


    assert ag.total_entities == len(entities)
    assert ag.total_instances == total_instances


# -------------------------- test quality parameter -------------------------- #


def test_quality_distributions():

    config = BaseConfig(
        size=10,
        prob_good=0.5,
        prob_noisy=0.4,
        prob_bad=0.3,
    )
    assert config._prob_weights == [0.5, 0.4, 0.3]


@pytest.mark.skip(
    "Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2"
)
def test_distributions_only_noisy():
    """It's not trivial to test that *all* values are noisy

    In the absence of a validation library, we will try to test this
    using regexp and good intentions for now"""

    config = BaseConfig(size=10, prob_good=0, prob_noisy=1, prob_bad=0)
    ag = AircraftGenerator(config=config)
    ag.populate()

    frequency_units_kinds = {"Flights", "Days", "Miles"}

    # we will check first that all kinds are not conformant
    noisy_kinds = (fo.frequencyunits for fo in ag.forecasted_orders)

    # but still they look like conformant values
    re_kind = re.compile(r"^\s*flights|days|miles\s*$", flags=re.I)

    for kind in noisy_kinds:
        assert kind not in frequency_units_kinds
        assert re_kind.search(kind)

    # we will then reconstruct them into proper values
    stripped_kinds = (kind.strip() for kind in noisy_kinds)
    rebuilt_kinds = (kind[0].upper() + kind[1:].lower() for kind in stripped_kinds)

    # check that these values are now valid
    for kind in rebuilt_kinds:
        assert kind in frequency_units_kinds


@pytest.mark.skip(
    "Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2"
)
def test_distributions_only_bad():
    """It's not trivial to test that *all* values are bad

    In the absence of a validation library, we will try to test this
    using regexp and good intentions for now"""

    config = BaseConfig(size=10, prob_good=0, prob_noisy=0, prob_bad=1)
    ag = AircraftGenerator(config=config)
    ag.populate()

    frequency_units_kinds = {"Flights", "Days", "Miles"}

    # we will check first that all kinds are not conformant
    bad_kinds = (fo.frequencyunits for fo in ag.forecasted_orders)

    # and that they don't look like conformant values
    re_kind = re.compile(r"^\s*flights|days|miles\s*$", flags=re.I)

    for kind in bad_kinds:
        assert kind not in frequency_units_kinds
        assert re_kind.search(kind) is None

    # we will then reconstruct them into proper values
    stripped_kinds = (kind.strip() for kind in bad_kinds)
    rebuilt_kinds = (kind[0].upper() + kind[1:].lower() for kind in stripped_kinds)

    # check that these values are now valid
    for kind in rebuilt_kinds:
        assert kind not in frequency_units_kinds
        assert re_kind.search(kind) is None


def test_distributions_only_good():
    """It's not trivial to test that *all* values are bad

    In the absence of a validation library, we will try to test this
    using regexp and good intentions for now"""

    config = BaseConfig(size=10, prob_good=1, prob_noisy=0, prob_bad=0)
    ag = AircraftGenerator(config=config)
    ag.populate()

    frequency_units_kinds = {"Flights", "Days", "Miles"}

    # we will check first that all kinds are not conformant
    good_kinds = (fo.frequencyunits for fo in ag.forecasted_orders)

    # and that they don't look like conformant values
    re_kind = re.compile(r"^Flights|Days|Miles$")

    for kind in good_kinds:
        assert kind in frequency_units_kinds
        assert re_kind.search(kind)

    # we will then reconstruct them into proper values
    stripped_kinds = (kind.strip() for kind in good_kinds)
    rebuilt_kinds = (kind[0].upper() + kind[1:].lower() for kind in stripped_kinds)

    # check that these values are still valid
    for kind in good_kinds:
        assert kind in frequency_units_kinds
        assert re_kind.search(kind)


@pytest.mark.skip(
    "Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2"
)
def test_distributions_mixed_qualities():
    """Again, it's not trivial to test this.

    In the absence of a validation library, we will try to test this
    using regexp and good intentions for now"""

    config = BaseConfig(size=100, prob_good=0.6, prob_noisy=0.3, prob_bad=0.1)

    # we will check first that all kinds are not conformant
    # and that they don't look like conformant values
    re_kind_good = re.compile(r"^Flights|Days|Miles$")
    re_kind_noisy = re.compile(r"^\s*flights|days|miles\s*$", flags=re.I)
    frequency_units_kinds = {"Flights", "Days", "Miles"}

    count_good = []
    count_noisy = []
    count_bad = []

    for _ in range(10):
        ag = AircraftGenerator(config=config)
        ag.populate()

        kinds = [fo.frequencyunits for fo in ag.forecasted_orders]

        _count_good = sum(1 for kind in kinds if re_kind_good.search(kind))

        count_good.append(_count_good)
        count_noisy.append(
            sum(1 for kind in kinds if re_kind_noisy.search(kind)) - _count_good
        )

        # if it does not match either of good or noisy, then it is bad
        count_bad.append(
            sum(
                1
                for kind in kinds
                if all(
                    [
                        re_kind_good.search(kind) is None,
                        re_kind_noisy.search(kind) is None,
                    ]
                )
            )
        )

    # assert that counts are approximately what we expect
    tol = 10
    assert mean(count_good) == pytest.approx(60, abs=tol)  # (100)*0.6 ± tol
    assert mean(count_noisy) == pytest.approx(30, abs=tol)  # (100)*0.3 ± tol
    assert mean(count_bad) == pytest.approx(10, abs=tol)  # (100)*0.1 ± tol
    assert (mean(count_good) + mean(count_noisy)) == pytest.approx(90, abs=tol)


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


    config.size = 100
    ag = AircraftGenerator(config=config)
    ag.populate()

    assert config._prob_weights == [1, 0, 0]

    # uno de los business rules dice que cada workorders por un aircraft debería
    # estar dentro de al menos un maintenance events 
    # (w.executiondate between starttime and starttime+duration).
    airc_regs_wo = [wo.aircraftregistration for wo in chain(ag.forecasted_orders, ag.tlb_orders)]
    airc_regs_me = [me.aircraftregistration for me in ag.operational_interruptions]

    # Maintenance event can include several work orders and each work order is 
    # inside one maintenance event. However, this reference is not explicit. 
    # It is represented as I said above by the same aircraft registration and 
    # the fact that the execution date of the work order is inside the time 
    # interval of the maintenance event (startdate, startdate + duration).

    assert airc_regs_me == airc_regs_wo



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

    wo_execution_date = [wo.executiondate for wo in chain(ag.tlb_orders, ag.forecasted_orders)]
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
    
    currently ~9900 out of 10000 rows don't pass this test
    """
    

    config = BaseConfig(size = 1000)
    config._prob_weights = [1, 0, 0]
    ag = AircraftGenerator(config=config)
    ag.populate()

    # fetch all airc. regs.
    aircraft_registrations = [f.aircraftregistration for f in ag.flight_slots]

    # paranoid check
    assert ag.config.size == config.size
    assert len(ag.flight_slots) == config.size

    for ar in aircraft_registrations:
        # fetch all flights with that ar code
        same_aircraft_flights = [f for f in ag.flight_slots if (f.aircraftregistration == ar and f.cancelled is False)]
        # check that the flights with this ar don't overlap
        if len(same_aircraft_flights) >= 2:
            for flight_1, flight_2 in permutations(same_aircraft_flights, 2):
                ts1 = flight_1.actualdeparture
                te1 = flight_1.actualarrival
                ts2 = flight_2.actualdeparture
                te2 = flight_2.actualarrival
                    
                min_end = min(te1, te2)
                max_start = max(ts1, ts2)

                assert not min_end > max_start
