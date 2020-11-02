import sqlalchemy as sa
from sqlalchemy import inspect


class UtilsMixin(object):
    """A mixin to implement a generic utilities"""

    def __repr__(self):        
        inspector = inspect(self.__class__)
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(
                [f"{c}={getattr(self, c)}" for c in inspector.attrs.keys()]
            ),
        )

    def as_dict(self):
        """return instance as a dictionary"""
        inspector = inspect(self.__class__)
        return {c: getattr(self, c) for c in inspector.attrs.keys() if not c.startswith("_")}
