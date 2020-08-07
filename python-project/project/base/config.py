from datetime import datetime
import typing as T
import attr

# ---------------------------------------------------------------------------- #
#                                  validators                                  #
# ---------------------------------------------------------------------------- #


def check_probability(instance, attribute, value):
    # see https://www.attrs.org/en/stable/examples.html#validators
    if not (0 < value < 1):
        raise ValueError("probability must be a float in range [0,1]")


@attr.s(auto_attribs=True)
class BaseConfig:
    """A configuration class to control the generation process"""

    seed: int = 42

    # ---------------------------------------------------------------------------- #
    #                                     sizes                                    #
    # ---------------------------------------------------------------------------- #

    size: int = 1000  # base size
    flight_slots_size: int = size
    maintenance_slots_size: int = size
    tlb_orders_size: int = size
    forecasted_orders_size: int = size
    # ois_events_size is controlled by flight_slots_size
    # maintenance_events_size is controlled by maintenance_slots_size
    max_attch_size: int = 1
    max_work_orders: int = 1

    # ---------------------------------------------------------------------------- #
    #                            other sensible defaults                           #
    # ---------------------------------------------------------------------------- #

    max_dur: int = 5
    max_delay: int = 40
    max_pas: int = 180
    min_pas: int = 90
    max_ccrew: int = 4
    min_ccrew: int = 3
    max_fcrew: int = 3
    min_fcrew: int = 2
    fleet_size: int = 20
    prob_flight_slot: float = attr.ib(0.4, validator=check_probability)
    prob_tlb: float = attr.ib(0.5, validator=check_probability)

    # ---------------------------------------------------------------------------- #
    #                              database parameters                             #
    # ---------------------------------------------------------------------------- #

    db_url: str = "postgresql://postgres:admin@localhost:54320/postgres"
    