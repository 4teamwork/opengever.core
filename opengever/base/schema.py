from collective.z3cform.datetimewidget.converter import DatetimeDataConverter
from collective.z3cform.datetimewidget.interfaces import DatetimeValidationError
from datetime import datetime
from tzlocal import get_localzone
from zope import schema
from zope.interface import implements


class ITZLocalDatetime(schema.interfaces.IDatetime):
    pass


class TZLocalDatetime(schema.Datetime):
    implements(ITZLocalDatetime)


class TZLocalDatetimeDataConverter(DatetimeDataConverter):

    def toFieldValue(self, value):
        for val in value:
            if not val:
                return self.field.missing_value

        try:
            value = map(int, value)
        except ValueError:
            raise DatetimeValidationError
        try:
            return get_localzone().localize(datetime(*value))
        except ValueError:
            raise DatetimeValidationError
