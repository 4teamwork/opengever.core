from datetime import timedelta
from opengever.task import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class Reminder(object):
    """Base class for reminders.

    Will never be persisted directly. Instead, it supports serialize() and
    deserialize() methods that handle serialization to/from a simple nested
    dictionary.
    """

    option_type = None
    option_title = None
    sort_order = None

    def __init__(self, params=None):
        if params is None:
            params = {}
        self.params = params

    @staticmethod
    def create(option_type, params=None):
        """Factory method to create Reminder instance based on option_type.
        """
        klass = REMINDER_TYPE_REGISTRY[option_type]
        return klass(params)

    def serialize(self):
        """Turn reminder instance's state into JSON serializable data.
        """
        data = {}
        data['option_type'] = self.option_type
        data['params'] = self.params
        return data

    @classmethod
    def deserialize(cls, reminder_data):
        """Construct reminder instance from serialized data dict.
        """
        return cls.create(**reminder_data)

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


TASK_REMINDER_TYPES = (
    ReminderSameDay,
    ReminderOneDayBefore,
    ReminderOneWeekBefore,
    ReminderBeginningOfWeek,
)

REMINDER_TYPE_REGISTRY = {
    klass.option_type: klass for klass in TASK_REMINDER_TYPES
}


def get_task_reminder_options_vocabulary():
    terms = []
    options = REMINDER_TYPE_REGISTRY.values()
    for option in sorted(options, key=lambda x: x.sort_order):
        terms.append(SimpleTerm(
            option.option_type, title=option.option_title))

    return SimpleVocabulary(terms)
