from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from opengever.task import _
from plone.restapi.serializer.converters import json_compatible
from zope.interface import Interface
from zope.schema import Date
from zope.schema import getFields
from zope.schema import ValidationError
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import WrongType
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class UnknownField(ValidationError):
    """Encountered an unexpected, extra field that's not part of the schema.
    """


class Reminder(object):
    """Base class for reminders.

    Will never be persisted directly. Instead, it supports serialize() and
    deserialize() methods that handle serialization to/from a simple nested
    dictionary.
    """

    option_type = None
    option_title = None
    sort_order = None
    schema = None

    def __init__(self, params=None):
        if params is None:
            params = {}

        self.validate_schema(params)
        self.params = deepcopy(params)

    @classmethod
    def validate_schema(cls, params, validate_types=True):
        """Simple schema validation.

        Once opengever.webactions.validation has been factored out, this can
        be updated to provide friendlier and more consistent validation.
        """
        fields = getFields(cls.schema) if cls.schema else {}

        # Check all required params are supplied
        missing = [field.getName() for field in fields.values()
                   if field.required and field.getName() not in params]
        if missing:
            raise RequiredMissing(missing[0])

        # Reject any unknown params
        unknown = [param for param in params if param not in fields]
        if unknown:
            raise UnknownField(unknown[0])

        # Validate parameter data types
        if validate_types:
            for name, value in params.items():
                field = fields.get(name)
                if not isinstance(value, field._type):
                    raise WrongType(name)

    @staticmethod
    def create(option_type, params=None):
        """Factory method to create Reminder instance based on option_type.
        """
        klass = REMINDER_TYPE_REGISTRY[option_type]
        return klass(params)

    def serialize(self, json_compat=False):
        """Turn reminder instance's state into a simple Python data structure.

        If json_compat is True, Dates will be represented as ISO 8601 strings
        for JSON compatibility.
        """
        data = {}
        data['option_type'] = self.option_type
        data['params'] = deepcopy(self.params)

        if json_compat:
            # Datetimes need some special love for JSON :-/
            data['params'] = json_compatible(data['params'])

        return data

    @classmethod
    def deserialize(cls, reminder_data):
        """Construct reminder instance from serialized data dict.

        If a parameter field is of `Date` type, both ISO 8601 strings
        (from JSON) as well as Python native date objects are supported.
        """
        option_type = reminder_data['option_type']
        params = deepcopy(reminder_data.get('params'))
        if params is None:
            params = {}

        target_class = REMINDER_TYPE_REGISTRY[option_type]
        target_class.validate_schema(params, validate_types=False)

        for name, value in params.items():
            field = target_class.schema[name]

            # Datetimes need some special love for JSON :-/
            if isinstance(field, Date) and isinstance(value, basestring):
                params[name] = datetime.strptime(value, '%Y-%m-%d').date()

        return cls.create(option_type, params=params)

    def calculate_trigger_date(self, deadline):
        """Compute on which date this reminder should be triggered.

        Needs to be implemented by the specific subclass.
        """
        raise NotImplementedError

    def __eq__(self, other):
        """Compare whether two reminder instances are equivalent.
        """
        return isinstance(other, self.__class__) and other.params == self.params


class ReminderSameDay(Reminder):

    option_type = 'same_day'
    option_title = _(u'reminder_option_title_today',
                     default="At the morging of the deadline")
    sort_order = 0

    def calculate_trigger_date(self, deadline):
        return deadline - timedelta(days=0)


class ReminderOneDayBefore(Reminder):

    option_type = 'one_day_before'
    option_title = _(u'reminder_option_title_one_day_before',
                     default="One day before deadline")
    sort_order = 1

    def calculate_trigger_date(self, deadline):
        return deadline - timedelta(days=1)


class ReminderOneWeekBefore(Reminder):

    option_type = 'one_week_before'
    option_title = _(u'reminder_option_title_one_week_before',
                     default="One week before deadline")
    sort_order = 3

    def calculate_trigger_date(self, deadline):
        return deadline - timedelta(days=7)


class ReminderBeginningOfWeek(Reminder):

    option_type = 'beginning_of_week'
    option_title = _(u'reminder_option_title_beginning_of_week',
                     default="At the beginning of the week of the deadline")
    sort_order = 2

    def calculate_trigger_date(self, deadline):
        return deadline - timedelta(days=deadline.weekday())


class ReminderOnDate(Reminder):

    option_type = 'on_date'
    option_title = _(u'reminder_option_title_on_date',
                     default="On a specific date")
    sort_order = 4

    class IOnDateParams(Interface):

        date = Date(
            title=u'Date on which the reminder shall trigger',
            required=True)

    schema = IOnDateParams

    def calculate_trigger_date(self, deadline):
        return self.params['date']


REMINDER_TYPES = (
    ReminderSameDay,
    ReminderOneDayBefore,
    ReminderOneWeekBefore,
    ReminderBeginningOfWeek,
    ReminderOnDate,
)

REMINDER_TYPE_REGISTRY = {
    klass.option_type: klass for klass in REMINDER_TYPES
}

# This type requires a special widget and would therefore break the UI
# until that widget is implemented. Remove this blacklist to have it show up.
REMINDER_TYPES_BLACKLISTED_FROM_UI = (ReminderOnDate, )


def get_task_reminder_options_vocabulary():
    terms = []
    options = REMINDER_TYPE_REGISTRY.values()
    for option in sorted(options, key=lambda x: x.sort_order):
        if option in REMINDER_TYPES_BLACKLISTED_FROM_UI:
            continue

        terms.append(SimpleTerm(
            option.option_type, title=option.option_title))

    return SimpleVocabulary(terms)
