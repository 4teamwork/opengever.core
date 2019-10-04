from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.task.reminder.interfaces import IReminderStorage
from opengever.task.reminder.interfaces import IReminderSupport
from plone import api
from zope.interface import implementer


@implementer(IReminderSupport)
class ReminderSupport(object):

    def set_reminder(self, reminder, user_id=None):
        """Sets a reminder for the given object for a specific user or for the
        current logged in user.

        A previously set reminder for the given user for the given object will
        be overridden by the new reminder-setting.
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
        """Get the mapping of userid -> reminder for all reminders
        (for all users) on the given obj.
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

    def get_reminders_of_potential_responsibles(self):
        """Get reminders of all responsible representatives.
        """
        representatives = [actor.userid for actor in
                           self.get_responsible_actor().representatives()]

        return {user_id: reminder
                for user_id, reminder in self.get_reminders().items()
                if user_id in representatives}

    def get_sql_reminder(self, user_id=None):
        """Get the sql-reminder for the given object for a specific user or
        for the current logged in user.

        Returns None, if no reminder is set.
        """
        user_id = user_id or api.user.get_current().getId()
        return ReminderSetting.query.filter(
            ReminderSetting.actor_id == user_id,
            ReminderSetting.task.has(task_id=self.get_sql_object().task_id)).first()

    def update_reminder_trigger_dates(self):
        """If the duedate of a task will change, we have to update the
        reminde-day of all reminders set for this object.
        """
        sql_task = self.get_sql_object()

        for reminder_setting in sql_task.reminder_settings:
            reminder = self.get_reminder(user_id=reminder_setting.actor_id)
            new_remind_day = reminder.calculate_trigger_date(sql_task.deadline)
            reminder_setting.remind_day = new_remind_day
