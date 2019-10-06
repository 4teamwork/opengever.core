from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask
from persistent.dict import PersistentDict
from zope.annotation import IAnnotations


TASK_REMINDER_ANNOTATIONS_KEY = 'opengever.task.task_reminder'


class MigrateTaskRemindersToNewStorageFormat(UpgradeStep):
    """Migrate task reminder annotations to new storage format.

    Old format:
    {'john.doe': 'same_day'}

    New format:
    {'john.doe': {'option_type': 'same_day', 'params': {}}}
    """

    def __call__(self):
        for task in self.objects({'object_provides': ITask.__identifier__},
                                 'Migrate task reminder annotations to new storage format'):
            self.migrate_reminder_annotations(task)

    def migrate_reminder_annotations(self, task):
        ann = IAnnotations(task)

        if TASK_REMINDER_ANNOTATIONS_KEY in ann:
            reminder_annotations = ann[TASK_REMINDER_ANNOTATIONS_KEY]

            for user_id, option_type in reminder_annotations.items():
                if isinstance(option_type, basestring):
                    new_entry = PersistentDict(
                        {'option_type': option_type,
                         'params': PersistentDict()})
                    reminder_annotations[user_id] = new_entry
