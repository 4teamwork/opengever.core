from opengever.base.utils import make_persistent
from opengever.task.reminder import Reminder
from opengever.task.reminder.interfaces import IReminderStorage
from persistent.dict import PersistentDict
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer


REMINDER_ANNOTATIONS_KEY = 'opengever.task.task_reminder'


@implementer(IReminderStorage)
@adapter(IDexterityContent)
class ReminderAnnotationStorage(object):

    def __init__(self, context):
        self.context = context

    def set(self, reminder, user_id=None):
        """Set a reminder on the adapted object.

        reminder -- The reminder to set
        user_id -- User to set the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """
        user_id = user_id or api.user.get_current().getId()
        assert isinstance(reminder, Reminder)
        reminder_data = reminder.serialize()
        self._set_user_annotation(user_id, make_persistent(reminder_data))

    def get(self, user_id=None):
        """Return reminder for adapted object, or None if no reminder exists.

        user_id -- User to get the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """
        user_id = user_id or api.user.get_current().getId()
        reminder_data = self._get_user_annotation(user_id)
        if reminder_data:
            return Reminder.deserialize(reminder_data)

    def list(self):
        """Return user_id -> reminder mapping of all reminders for adapted obj.
        """
        reminders_by_user = self._annotation_storage()
        reminders = {user_id: Reminder.deserialize(reminder_data)
                     for user_id, reminder_data in reminders_by_user.items()}
        return reminders

    def clear(self, user_id=None):
        """Clear an existing reminder.

        user_id -- User to clear the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """
        user_id = user_id or api.user.get_current().getId()
        storage = self._annotation_storage()
        if user_id in storage:
            del storage[user_id]

    def _annotation_storage(self, create_if_missing=False):
        annotations = IAnnotations(self.context)
        # Avoid writes on read
        if REMINDER_ANNOTATIONS_KEY not in annotations and create_if_missing:
            annotations[REMINDER_ANNOTATIONS_KEY] = PersistentDict()

        return annotations.get(REMINDER_ANNOTATIONS_KEY, {})

    def _set_user_annotation(self, user_id, value):
        assert isinstance(user_id, str)
        storage = self._annotation_storage(create_if_missing=True)
        storage[user_id] = value

    def _get_user_annotation(self, user_id):
        return self._annotation_storage().get(user_id)
