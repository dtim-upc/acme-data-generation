from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker

from acme_data_generation.models.declarative import AIMSBase, AMOSBase


# create a configured "Session" class
Session = sessionmaker()


def get_session(engine: Engine):
    session = Session(bind=engine)
    return session


def delete_all(engine: Engine) -> None:
    AIMSBase.metadata.drop_all(engine)
    AMOSBase.metadata.drop_all(engine)
    # amos_meta.drop_all(engine)
    # aims_meta.drop_all(engine)


def create_all(engine: Engine) -> None:
    AIMSBase.metadata.create_all(engine)
    AMOSBase.metadata.create_all(engine)
    # amos_meta.create_all(engine)
    # aims_meta.create_all(engine)
