from ftw.upgrade import UpgradeStep


class SyncTaskReminders(UpgradeStep):
    """Sync task reminders.
    """

    def __call__(self):
        query = {'object_provides': 'opengever.task.task.ITask',
                 'review_state': 'task-state-in-progress'}
        for task in self.objects(query, "Sync task reminders."):
            task.sync_reminders()
