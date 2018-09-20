from datetime import date
from datetime import timedelta
from opengever.task import _


def day_delta(delta):
    """Returns a function, calculating a date with the given day-delta.
    """
    def calc(date_):
        return date_ - timedelta(days=delta)

    return calc


def last_monday(date_):
    """Returns a function, getting the last monday.
    """
    return date_ - timedelta(days=date_.weekday())


class ReminderOption(object):

    def __init__(self, option_type, option_title, remind_day_func):
        self.option_type = option_type
        self.option_title = option_title

        self._remind_day_func = remind_day_func

    def calculate_remind_on(self, deadline):
        return self._remind_day_func(deadline)


TASK_REMINDER_SAME_DAY = ReminderOption(
    option_type='same_day',
    option_title=_(u'reminder_option_title_today',
                   default="At the morging of the deadline"),
    remind_day_func=day_delta(0))

TASK_REMINDER_ONE_DAY_BEFORE = ReminderOption(
    option_type='one_day_before',
    option_title=_(u'reminder_option_title_one_day_before',
                   default="One day before deadline"),
    remind_day_func=day_delta(1))

TASK_REMINDER_ONE_WEEK_BEFORE = ReminderOption(
    option_type='one_week_before',
    option_title=_(u'reminder_option_title_one_week_before',
                   default="One week before deadline"),
    remind_day_func=day_delta(7))

TASK_REMINDER_BEGINNING_OF_WEEK = ReminderOption(
    option_type='beginning_of_week',
    option_title=_(u'reminder_option_title_beginning_of_week',
                   default="At the beginning of the week of the deadline"),
    remind_day_func=last_monday)

TASK_REMINDER_OPTIONS = {
    TASK_REMINDER_SAME_DAY.option_type: TASK_REMINDER_SAME_DAY,
    TASK_REMINDER_ONE_DAY_BEFORE.option_type: TASK_REMINDER_ONE_DAY_BEFORE,
    TASK_REMINDER_ONE_WEEK_BEFORE.option_type: TASK_REMINDER_ONE_WEEK_BEFORE,
    TASK_REMINDER_BEGINNING_OF_WEEK.option_type: TASK_REMINDER_BEGINNING_OF_WEEK,
}
