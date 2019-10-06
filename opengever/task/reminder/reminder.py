from opengever.task.reminder.interfaces import IReminderStorage
from opengever.task.reminder.interfaces import IReminderSupport
from zope.interface import implementer


@implementer(IReminderSupport)
class ReminderSupport(object):
    """Implements support for reminders for a particular content type.

    A farily generic implementation might be possible in the future,
    but for now this is only used for the Task type.

    This interface could be implemented by an adapter, but for now we'll have
    the Task class directly implement it itself, because then the methods
    can be invoked directly on the task object and the code is more readable.
    """

    def set_reminder(self, reminder, user_id=None):
        """Sets a reminder for the given object for a specific user or for the
        current logged in user.

        A previously set reminder for the given user for the given object will
        be overridden by the new reminder.
        """
        storage = IReminderStorage(self)
        storage.set(reminder, user_id)

    def get_reminder(self, user_id=None):
        """Get the reminder for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        storage = IReminderStorage(self)
        return storage.get(user_id)

    def get_reminders(self):
        """Get all reminders for this obj as a {userid: reminder} mapping.
        """
        storage = IReminderStorage(self)
        return storage.list()

    def clear_reminder(self, user_id=None):
        """Removes a registered reminder for the given object for a specific
        user or for the current logged in user.
        """
        storage = IReminderStorage(self)
        storage.clear(user_id)


class TaskReminderSupport(ReminderSupport):
    """Aspects of reminder-support that are specific to tasks.
    """

    def get_reminders_of_potential_responsibles(self):
        """Get reminders of all responsible representatives.
        """
        representatives = [actor.userid for actor in
                           self.get_responsible_actor().representatives()]

        return {user_id: reminder
                for user_id, reminder in self.get_reminders().items()
                if user_id in representatives}

    def update_reminder_trigger_dates(self):
        """If the due date of a task changes, we have to update the
        trigger date of all reminders set for this object.
        """
        sql_task = self.get_sql_object()

        for reminder_setting in sql_task.reminder_settings:
            reminder = self.get_reminder(user_id=reminder_setting.actor_id)
            new_trigger_date = reminder.calculate_trigger_date(sql_task.deadline)
            reminder_setting.remind_day = new_trigger_date
