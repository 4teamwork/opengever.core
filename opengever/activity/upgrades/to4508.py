from ftw.upgrade import UpgradeStep
from opengever.activity import notification_center
from opengever.globalindex.model.task import Task


class ReRegisterWatchers(UpgradeStep):

    def __call__(self):
        self.center = notification_center()

        query = {'object_provides': 'opengever.task.task.ITask',
                 'review_state': Task.PENDING_STATES}
        for task in self.objects(query, "Reregister watchers for all tasks."):
            self.register_watchers(task)

    def register_watchers(self, task):
        self.center.add_task_responsible(task, task.responsible)
        self.center.add_task_issuer(task, task.issuer)
