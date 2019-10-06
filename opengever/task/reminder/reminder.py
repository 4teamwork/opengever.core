from datetime import date
from opengever.base.model import create_session
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.task.activities import TaskReminderActivity
from opengever.task.reminder import TASK_REMINDER_OPTIONS
from opengever.task.reminder.interfaces import IReminderStorage
from plone import api
from zope.globalrequest import getRequest


class TaskReminder(object):

    def __init__(self):
        self.session = create_session()

    def set_reminder(self, obj, option, user_id=None):
        """Sets a reminder for the given object for a specific user or for the
        current logged in user.

        A previously set reminder for the given user for the given object will
        be overridden by the new reminder-setting.

        arguments:
        obj -- the object for which the reminder should be set
        option -- a TASK_REMINDER_OPTIONS option
        """
        user_id = user_id or api.user.get_current().getId()
        storage = IReminderStorage(obj)
        storage.set(option.option_type, user_id)

    def get_reminder(self, obj, user_id=None):
        """Get the reminder-option object for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        user_id = user_id or api.user.get_current().getId()
        storage = IReminderStorage(obj)
        reminder_data = storage.get(user_id)
        if reminder_data:
            return TASK_REMINDER_OPTIONS.get(reminder_data['option_type'])

    def get_reminders(self, obj):
        """Get the reminder-option object for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        storage = IReminderStorage(obj)
        return {actor: TASK_REMINDER_OPTIONS.get(reminder_data['option_type'])
                for actor, reminder_data in storage.list().items()}

    def get_reminders_of_potential_responsibles(self, obj):
        """Get reminders of all responsible representatives.
        """
        representatives = [actor.userid for actor in
                           obj.get_responsible_actor().representatives()]

        data = {}
        for userid, reminder in self.get_reminders(obj).items():
            if userid in representatives:
                data[userid] = reminder.option_type
        return data

    def clear_reminder(self, obj, user_id=None):
        """Removes a registered reminder for the given object for a specific
        user or for the current logged in user.
        """
        user_id = user_id or api.user.get_current().getId()
        storage = IReminderStorage(obj)
        storage.clear(user_id)

    def create_reminder_notifications(self):
        """Creates an activity and the related notification for set reminders.
        """
        query = ReminderSetting.query.filter(
            ReminderSetting.remind_day == date.today())

        for reminder in query.all():
            TaskReminderActivity(reminder.task, getRequest()).record(reminder.actor_id)

        return query.count()

    def recalculate_remind_day_for_obj(self, obj):
        """If the duedate of a task will change, we have to update the
        reminde-day of all reminders set for this object.
        """
        map(lambda reminder: reminder.update_remind_day(),
            obj.get_sql_object().reminder_settings)
