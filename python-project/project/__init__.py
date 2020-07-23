from sqlalchemy import create_engine
from sqlalchemy import inspect

from .models.aims import Flight

if __name__ == "__main__":
    engine = create_engine("postgresql://postgres:admin@localhost:54320/postgres")
    insp = inspect(Flight)

    # select *
    result = engine.execute('SELECT * FROM "AIMS".flights')
    print(result)

    for _r in result:
        print(_r)
