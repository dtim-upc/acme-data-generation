from datetime import datetime
import typing as T
import attr


@attr.s(auto_attribs=True)
class BaseConfig:
    """A configuration class to control the generation process"""

    def validate(self):
        if not (0 < self.PROB_TLB < 1):
            raise ValueError("probability must be a float in range [0,1]")

        if not (0 < self.PROB_FLIGHT_SLOT < 1):
            raise ValueError("probability must be a float in range [0,1]")

    SEED: int = 42
    SIZE: int = 1000  # number of rows of the CSV
    MAX_DUR: int = 5
    MAX_DELAY: int = 40
    MAX_PAS: int = 180
    MIN_PAS: int = 90
    MAX_CCREW: int = 4
    MIN_CCREW: int = 3
    MAX_FCREW: int = 3
    MIN_FCREW: int = 2
    FLEET_SIZE: int = 20
    PROB_FLIGHT_SLOT = 0.4
    PROB_TLB = 0.5
    MAX_ATTCH_SIZE: int = 1
    MAX_WORK_ORDERS: int = 1
