from opengever.ogds.models import BASE
from opengever.ogds.models.declarative import query_base
from sqlalchemy import types
from z3c.saconfig import named_scoped_session
import pytz


Session = named_scoped_session('opengever')

BASE.session = Session
Base = query_base(Session)


def get_tables(table_names):
    tables = Base.metadata.tables
    return [tables.get(table_name) for table_name in table_names]


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """
    return Session()


class UTCDateTime(types.TypeDecorator):
    """Sqlalchemy does not support timezone aware datetimes for Sqlite and
    MySQL backend. Therefore we have to ensure that timezone aware datetimes
    are returned.
    """

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(pytz.UTC)

    def process_result_value(self, value, engine):
        if value is not None:
            if value.tzinfo is None:
                # We manually add the UTC timezone, only needed for the DB
                # backend who does not support timezone aware datetime.
                value = pytz.utc.localize(value)
            return value
