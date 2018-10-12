from datetime import date
from opengever.base.model import create_session
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.task.activities import TaskReminderActivity
from opengever.task.reminder import TASK_REMINDER_OPTIONS
from persistent.dict import PersistentDict
from plone import api
from zope.annotation import IAnnotations
from zope.globalrequest import getRequest

TASK_REMINDER_ANNOTATIONS_KEY = 'opengever.task.task_reminder'


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
        self._set_reminder_setting_in_annotation(obj, user_id, option)
        self._set_reminder_setting_in_globalindex(obj, user_id, option)

    def get_reminder(self, obj, user_id=None):
        """Get the reminder-option object for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        user_id = user_id or api.user.get_current().getId()
        return TASK_REMINDER_OPTIONS.get(
            self._get_user_annotation(obj, user_id))

    def get_reminders(self, obj):
        """Get the reminder-option object for the given object for a specific
        user or for the current logged in user.

        Returns None, if no reminder is set.
        """
        storage = self._annotation_storage(obj)
        return {actor: TASK_REMINDER_OPTIONS.get(value)
                for actor, value in storage.items()}

    def get_sql_reminder(self, obj, user_id=None):
        """Get the sql-reminder for the given object for a specific user or
        for the current logged in user.

        Returns None, if no reminder is set.
        """
        user_id = user_id or api.user.get_current().getId()
        return ReminderSetting.query.filter(
            ReminderSetting.actor_id == user_id,
            ReminderSetting.task.has(task_id=obj.get_sql_object().task_id)).first()

    def clear_reminder(self, obj, user_id=None):
        """Removes a registered reminder for the given object for a specific
        user or for the current logged in user.
        """
        user_id = user_id or api.user.get_current().getId()
        self._clear_reminder_setting_in_annotation(obj, user_id)
        self._clear_reminder_setting_in_sql(obj, user_id)

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

    def _set_reminder_setting_in_annotation(self, obj, user_id, option):
        self._set_user_annotation(obj, user_id, option.option_type)

    def _set_reminder_setting_in_globalindex(self, obj, user_id, option):
        self._clear_reminder_setting_in_sql(obj, user_id)
        self.session.add(ReminderSetting(
            task_id=obj.get_sql_object().task_id,
            actor_id=user_id,
            option_type=option.option_type,
            remind_day=option.calculate_remind_on(obj.deadline)
            ))

    def _clear_reminder_setting_in_annotation(self, obj, user_id):
        storage = self._annotation_storage(obj)
        if user_id in storage:
            del storage[user_id]

    def _clear_reminder_setting_in_sql(self, obj, user_id):
        current_reminder = self.get_sql_reminder(obj, user_id)
        if current_reminder:
            self.session.delete(current_reminder)

    def _annotation_storage(self, obj):
        annotations = IAnnotations(obj)
        if TASK_REMINDER_ANNOTATIONS_KEY not in annotations:
            annotations[TASK_REMINDER_ANNOTATIONS_KEY] = PersistentDict()

        return annotations.get(TASK_REMINDER_ANNOTATIONS_KEY)

    def _set_user_annotation(self, obj, user_id, value):
        storage = self._annotation_storage(obj)
        storage[user_id] = value

    def _get_user_annotation(self, obj, user_id):
        return self._annotation_storage(obj).get(user_id)
