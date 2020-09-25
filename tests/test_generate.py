import pytest
import typing as T
from statistics import mean
import re

from project.scripts.generate import AircraftGenerator
from project.base.config import BaseConfig


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

    assert len(ag.slots) == total_size
    assert len(ag.maintenance_slots) + len(ag.flight_slots) == len(ag.slots)

    assert len(ag.maintenance_slots) == size
    assert len(ag.flight_slots) == size


@pytest.mark.parametrize("size", [10, 100, 1000])
def test_workorders_size(config, size):

    config.tlb_orders_size = size
    config.forecasted_orders_size = size
    total_size = 2 * size

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert len(ag.tlb_orders) == size
    assert len(ag.forecasted_orders) == size
    assert len(ag.workorders) == total_size
    assert len(ag.tlb_orders) + len(ag.forecasted_orders) == len(ag.workorders)


@pytest.mark.parametrize("attch_size", [1, 2])
@pytest.mark.parametrize("oi_size", [10, 100, 1000])
def test_attachments_size(config, oi_size, attch_size):

    # ois_size is controlled by flight_slots_size
    # maintenance_events_size is controlled by maintenance_slots_size

    config.flight_slots_size = oi_size
    config.max_attch_size = attch_size

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
        max_attch_size=1,
        max_work_orders=1,
    )

    ag = AircraftGenerator(config=config)
    ag.populate()

    assert config.size == custom_size
    assert config.flight_slots_size == custom_size
    assert config.maintenance_slots_size == custom_size
    assert config.tlb_orders_size == custom_size
    assert config.forecasted_orders_size == custom_size
    assert config.max_attch_size == 1
    assert config.max_work_orders == 1

    total_instances = sum(
        [
            len(ag.flight_slots),
            len(ag.maintenance_slots),
            len(ag.slots),
            len(ag.operational_interruptions),
            len(ag.maintenance_events),
            len(ag.manufacturers),
            len(ag.workorders),
            len(ag.tlb_orders),
            len(ag.forecasted_orders),
            len(ag.attachments),
        ]
    )

    assert ag.total_entities == 10
    assert ag.total_instances == total_instances


# -------------------------- test quality parameter -------------------------- #


def test_quality_distributions():

    config = BaseConfig(size=10, prob_good=0.5, prob_noisy=0.4, prob_bad=0.3,)
    assert config._prob_weights == [0.5, 0.4, 0.3]


@pytest.mark.skip("Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2")
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


@pytest.mark.skip("Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2")
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


@pytest.mark.skip("Test needs an update, see https://github.com/diegoquintanav/acme-data-generation/issues/2")
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

