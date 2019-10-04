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
        user_id = user_id or api.user.get_current().getId()
        self._set_user_annotation(user_id, make_persistent(reminder.serialize()))

    def get(self, user_id=None):
        user_id = user_id or api.user.get_current().getId()
        reminder_dict = self._get_user_annotation(user_id)
        if reminder_dict:
            return Reminder.deserialize(reminder_dict)

    def list(self):
        reminders_by_user = self._annotation_storage()
        reminders = {user_id: Reminder.deserialize(reminder_dict)
                     for user_id, reminder_dict in reminders_by_user.items()}
        return reminders

    def clear(self, user_id=None):
        user_id = user_id or api.user.get_current().getId()
        self._clear_reminder_setting_in_annotation(user_id)

    def _clear_reminder_setting_in_annotation(self, user_id):
        storage = self._annotation_storage()
        if user_id in storage:
            del storage[user_id]

    def _annotation_storage(self, create_if_missing=False):
        annotations = IAnnotations(self.context)
        if REMINDER_ANNOTATIONS_KEY not in annotations and create_if_missing:
            annotations[REMINDER_ANNOTATIONS_KEY] = PersistentDict()

        return annotations.get(REMINDER_ANNOTATIONS_KEY, {})

    def _set_user_annotation(self, user_id, value):
        storage = self._annotation_storage(create_if_missing=True)
        storage[user_id] = value

    def _get_user_annotation(self, user_id):
        return self._annotation_storage().get(user_id)
