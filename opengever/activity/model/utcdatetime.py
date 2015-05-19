from sqlalchemy import types
import pytz


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
