from collective.z3cform.datetimewidget.converter import DatetimeDataConverter
from collective.z3cform.datetimewidget.interfaces import DatetimeValidationError
from datetime import datetime
from opengever.base.date_time import as_utc
from tzlocal import get_localzone
from zope import schema
from zope.interface import implements


class IUTCDatetime(schema.interfaces.IDatetime):
    pass


class UTCDatetime(schema.Datetime):
    implements(IUTCDatetime)


class UTCDatetimeDataConverter(DatetimeDataConverter):
    """Return timezone aware datetimes.

    The users input is timezone naive. Since there are no timezone settings
    the input is localized in the *servers* timezone and then converted to UTC.

    """
    def toFieldValue(self, value):
        for val in value:
            if not val:
                return self.field.missing_value

        try:
            value = map(int, value)
        except ValueError:
            raise DatetimeValidationError
        try:
            local_dt = get_localzone().localize(datetime(*value))
            return as_utc(local_dt)
        except ValueError:
            raise DatetimeValidationError
