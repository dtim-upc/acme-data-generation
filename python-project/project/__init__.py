from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine

from project.models.classic import aims_meta, amos_meta
from project.models import AIMSBase, AMOSBase


def delete_all(engine: Engine):
    # AIMSBase.metadata.drop_all(engine)
    # AMOSBase.metadata.drop_all(engine)

    aims_meta.drop_all(engine)
    amos_meta.drop_all(engine)


def create_all(engine: Engine):
    # AIMSBase.metadata.create_all(engine)
    # AMOSBase.metadata.create_all(engine)

    aims_meta.create_all(engine)
    amos_meta.create_all(engine)


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
