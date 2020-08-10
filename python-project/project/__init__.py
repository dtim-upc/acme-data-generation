import logging

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine

logging.basicConfig(level=logging.INFO)

# from project.models.classic import aims_meta, amos_meta
# from project.models.declarative import AIMSBase, AMOSBase
from project.base.config import BaseConfig
from project.scripts.db_utils import create_all, delete_all, get_session
from project.scripts.generate import AircraftGenerator

if __name__ == "__main__":

    config = BaseConfig(size=10)
    engine = create_engine(config.db_url, echo=False)

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

    session = get_session(engine)
    ag = AircraftGenerator(config)
    ag.populate()
    ag.to_sql(session)

    delete_all(engine)

