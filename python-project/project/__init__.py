from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine

from project.models.classic import aims_meta, amos_meta
from project.models.declarative import AIMSBase, AMOSBase
from project.scripts.db_utils import create_all, delete_all



if __name__ == "__main__":
    engine = create_engine(
        "postgresql://postgres:admin@localhost:54320/postgres", echo=True
    )

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
