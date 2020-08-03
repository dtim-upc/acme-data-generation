from pydantic import BaseModel
from project.providers import fake



class Manufacturer(BaseModel):
    aircraft_reg_code: str
    manufacturer_serial_number: str
    aircraft_model: str
    manufacturer: str


class Reporter(BaseModel):
    reporteurid: str
    airport: str

if __name__ == "__main__":
    print(fake.fleet(10))