from opengever.base.model import create_session
from opengever.task.reminder.interfaces import IReminderStorage


class TaskReminder(object):

    def __init__(self):
        self.session = create_session()

    def set_reminder(self, obj, reminder, user_id=None):
        """Sets a reminder for the given object for a specific user or for the
        current logged in user.

        A previously set reminder for the given user for the given object will
        be overridden by the new reminder.
        """
        storage = IReminderStorage(obj)
        storage.set(reminder, user_id)

    def get_reminder(self, obj, user_id=None):
        """Get the reminder for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        storage = IReminderStorage(obj)
        return storage.get(user_id)

    def get_reminders(self, obj):
        """Get all reminders for this obj as a {userid: reminder} mapping.
        """
        storage = IReminderStorage(obj)
        return storage.list()

    def get_reminders_of_potential_responsibles(self, obj):
        """Get reminders of all responsible representatives.
        """
        representatives = [actor.userid for actor in
                           obj.get_responsible_actor().representatives()]

        return {user_id: reminder
                for user_id, reminder in self.get_reminders(obj).items()
                if user_id in representatives}

    def clear_reminder(self, obj, user_id=None):
        """Removes a registered reminder for the given object for a specific
        user or for the current logged in user.
        """
        storage = IReminderStorage(obj)
        storage.clear(user_id)

    def recalculate_remind_day_for_obj(self, obj):
        """If the duedate of a task will change, we have to update the
        reminde-day of all reminders set for this object.
        """
        sql_task = obj.get_sql_object()

        for reminder_setting in sql_task.reminder_settings:
            reminder = self.get_reminder(obj, user_id=reminder_setting.actor_id)
            new_remind_day = reminder.calculate_trigger_date(sql_task.deadline)
            reminder_setting.remind_day = new_remind_day
