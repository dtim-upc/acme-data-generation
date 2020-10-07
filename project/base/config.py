from datetime import datetime
import typing as T
import attr

# ---------------------------------------------------------------------------- #
#                                  validators                                  #
# ---------------------------------------------------------------------------- #


def check_probability(instance, attribute, value):
    # see https://www.attrs.org/en/stable/examples.html#validators
    if not (0 <= value <= 1):
        raise ValueError("probability must be a float in range [0,1]")


@attr.s(auto_attribs=True)
class BaseConfig:
    """A configuration class to control the generation process"""

    seed: int = 42

    # ---------------------------------------------------------------------------- #
    #                                     sizes                                    #
    # ---------------------------------------------------------------------------- #

    size: int = 1000  # base size
    flight_slots_size: int = None
    maintenance_slots_size: int = None
    maintenance_events_size: int = None
    tlb_orders_size: int = None
    forecasted_orders_size: int = None
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
    #                              randomness controls                             #
    # ---------------------------------------------------------------------------- #

    prob_good: float = attr.ib(1.0, validator=check_probability)
    prob_noisy: float = attr.ib(0.0, validator=check_probability)
    prob_bad: float = attr.ib(0.0, validator=check_probability)

    # ---------------------------------------------------------------------------- #
    #                              database parameters                             #
    # ---------------------------------------------------------------------------- #

    db_url: str = "postgresql://postgres:admin@localhost:54320/postgres"

    # https://www.attrs.org/en/stable/examples.html?highlight=attrs_post_init#other-goodies
    def __attrs_post_init__(self):

        # if user did not set custom sizes, then attempt to make them all of
        # them equal to some custom size
        if self.flight_slots_size is None:
            self.flight_slots_size = self.size
        if self.maintenance_slots_size is None:
            self.maintenance_slots_size = self.size
        if self.maintenance_events_size is None:
            self.maintenance_events_size = self.size

        self._prob_weights = [self.prob_good, self.prob_noisy, self.prob_bad]
