from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import exc as orm_exc


def query_property():
    class query(object):
        def __get__(s, instance, owner):
            try:
                mapper = class_mapper(owner)
                if mapper:
                    session = owner.session
                    query_cls = owner.query_cls
                    # custom query class
                    if query_cls:
                        return query_cls(mapper, session=session.registry())
                    # session's configured query class
                    else:
                        return session.registry().query(mapper)
            except orm_exc.UnmappedClassError:
                return None
    return query()


def query_base(session=None):
    """Create a base class that queries the provided session."""

    class QueryBase(object):
        """Class that contains query functions."""

        session = None
        query_cls = None
        query = query_property()

        @classmethod
        def get_by(cls, *args, **kwargs):
            """
            Returns the first instance of this class matching the given
            criteria.

            This is a shorthand for:
            Session.query(MyClass).filter_by(...).first()
            """
            return cls.query.filter_by(*args, **kwargs).first()

        @classmethod
        def get(cls, *args, **kwargs):
            """
            Return the instance of this class based on the given identifier,
            or None if not found.

            This is a shorthand for:
            session.query(MyClass).get(...)
            """
            return cls.query.get(*args, **kwargs)

        @classmethod
        def get_one(cls, *args, **kwargs):
            """
            Returns one instance of this class matching the given criteria.

            This is a shorthand for:
            session.query(MyClass).filter_by(...).one()
            """
            return cls.query.filter_by(*args, **kwargs).one()

        @classmethod
        def _count_attribute(cls):
            """Return an attribute used for the improved count queries."""

            prim_key = class_mapper(cls).primary_key
            assert prim_key, 'no primary key for class {}'.format(cls.__name__)
            return prim_key[0]

        @classmethod
        def count(cls):
            """Helper for a nice count without a subquery."""

            return cls.session.query(
                func.count(cls._count_attribute())).scalar()

    if session:
        QueryBase.session = session

    return declarative_base(cls=QueryBase)
