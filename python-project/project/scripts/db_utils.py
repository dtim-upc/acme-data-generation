from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.base import Engine

# from project.models.classic import aims_meta, amos_meta
from project.models.declarative import AIMSBase, AMOSBase


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
