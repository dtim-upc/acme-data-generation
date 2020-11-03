import sqlalchemy as sa
from sqlalchemy import inspect


class UtilsMixin(object):
    """A mixin to implement a generic utilities"""

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join([f"{k}={v}" for k, v in self.as_dict().items()]),
        )

    def as_dict(self):
        """return instance as a dictionary"""
        inspector = inspect(self.__class__)
        return {
            c: getattr(self, c) for c in inspector.attrs.keys() if c not in {"type", "_sa_polymorphic_on"}
        }
