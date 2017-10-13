from collective.z3cform.datetimewidget.interfaces import DatetimeValidationError
from ftw.datepicker.converter import DateTimeDataConverter
from opengever.base.date_time import as_utc
from tzlocal import get_localzone
from zope import schema
from zope.interface import implements
from zope.schema.interfaces import IChoice


class IUTCDatetime(schema.interfaces.IDatetime):
    pass


class UTCDatetime(schema.Datetime):
    implements(IUTCDatetime)


class UTCDatetimeDataConverter(DateTimeDataConverter):
    """Return timezone aware datetimes.

    The users input is timezone naive. Since there are no timezone settings
    the input is localized in the *servers* timezone and then converted to UTC.

    """
    def toFieldValue(self, value):
        value = super(UTCDatetimeDataConverter, self).toFieldValue(value)
        if value is None:
            return value

        try:
            local_dt = get_localzone().localize(value)
            return as_utc(local_dt)
        except ValueError:
            raise DatetimeValidationError


class ITableChoice(IChoice):
    """Marker interface for table-choice fields."""


class TableChoice(schema.Choice):
    """Custom choice field for table-based widgets.

    Can be configured with a tuple of additional columns to be rendered.
    The column configuration must be in the format that is required by
    ftw.table's ITableGenerator.

    The optional configuration argument "vocabulary_depends_on" accepts
    a list of field names which influence the result of the table.
    This allows the widget to be reloaded automatically when the here
    listed fields change its values.
    """
    implements(ITableChoice)

    def __init__(self, columns=tuple(), vocabulary_depends_on=(), **kwargs):
        self.columns = columns
        self.vocabulary_depends_on = vocabulary_depends_on
        super(TableChoice, self).__init__(**kwargs)
