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
    flight_slots_size: T.Optional[int] = None
    maintenance_slots_size: T.Optional[int] = None
    tlb_orders_size: T.Optional[int] = None
    forecasted_orders_size: T.Optional[int] = None
    work_packages_size: T.Optional[int] = None
    # ois_events_size is controlled by flight_slots_size
    # maintenance_events_size is controlled by maintenance_slots_size
    max_attach_size: int = 1
    max_work_packages: int = 1
    max_work_orders: int = 1
    proba_forecast_order: float = 0.5

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
    personnel_list_size: int = 500
    prob_flight_slot: float = attr.ib(0.4, validator=check_probability)
    prob_tlb: float = attr.ib(0.5, validator=check_probability)

    # ---------------------------------------------------------------------------- #
    #                              randomness controls                             #
    # ---------------------------------------------------------------------------- #

    prob_noisy: T.Optional[float] = None
    prob_bad: T.Optional[float] = None
    prob_good: T.Optional[float] = None

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
        if self.tlb_orders_size is None:
            self.tlb_orders_size = self.size
        if self.forecasted_orders_size is None:
            self.forecasted_orders_size = self.size
        if self.work_packages_size is None:
            self.work_packages_size = self.size

        self._prob_weights = [self.prob_good, self.prob_noisy, self.prob_bad]

        # we want to check that probabilities are consistent
        if all(x is None for x in self._prob_weights):
            self.prob_good = 1
            self.prob_bad = 0
            self.prob_noisy = 0
       
        if self.prob_good is None:
            if self.prob_noisy is None:
                self.prob_good = 1 - self.prob_bad
                self.prob_noisy = 0
            else:
                self.prob_good = 1 - self.prob_bad - self.prob_noisy

        if self.prob_bad is None:
            if self.prob_noisy is None:
                self.prob_bad = 1 - self.prob_good
                self.prob_noisy = 0
            else:
                self.prob_bad = 1 - self.prob_good - self.prob_noisy

        if self.prob_noisy is None:
            if self.prob_bad is None:
                self.prob_noisy = 1 - self.prob_good
                self.prob_bad = 0
            else:
                self.prob_noisy = 1 - self.prob_good - self.prob_bad

        self._prob_weights = [self.prob_good, self.prob_noisy, self.prob_bad]

        assert sum(self._prob_weights) == 1, "Probabilities must add to 1"


        