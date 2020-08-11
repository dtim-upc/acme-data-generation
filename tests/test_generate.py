import pytest
import typing as T
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

