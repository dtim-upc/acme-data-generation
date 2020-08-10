from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine


# from project.models.classic import aims_meta, amos_meta
# from project.models.declarative import AIMSBase, AMOSBase
from project.base.config import BaseConfig
from project.scripts.db_utils import create_all, delete_all, get_session
from project.providers import fake


if __name__ == "__main__":

    config = BaseConfig()
    engine = create_engine(config.db_url, echo=True)

    # create session
    delete_all(engine)
    create_all(engine)

    # select *
    result = engine.execute(
        """
select 
  * 
from 
  pg_catalog.pg_tables 
where 
  schemaname != 'information_schema' 
  and schemaname != 'pg_catalog';"""
    )

    for _r in result:
        print(_r)

    # attempt to create an instance using the classical mappings
    fs = fake.flight_slot()

    session = get_session(engine)

    session.add(fs)
    session.commit()
