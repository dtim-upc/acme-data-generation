import typing as T
import attr

# fmt: on
@attr.s(auto_attribs=True)
class Manufacturer(object):
    aircraft_reg_code: T.Optional[str]
    manufacturer_serial_number: T.Optional[str]
    aircraft_model: T.Optional[str]
    aircraft_manufacturer: T.Optional[str]

    def as_dict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True)
class Reporter(object):
    reporteurid: T.Optional[str]
    airport: T.Optional[str]

    def as_dict(self):
        return attr.asdict(self)
