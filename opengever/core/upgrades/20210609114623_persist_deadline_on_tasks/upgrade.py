from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask


class PersistDeadlineOnTasks(UpgradeStep):
    """Persist deadline on tasks.
    """

    deferrable = True

    def is_deadline_persisted(self, obj):
        if obj._p_changed is None:
            # Object is a ghost, we need to make sure it gets loaded by
            # accessing any attribute. Accessing __dict__ does not trigger
            # loading of the object.
            obj.created()
        return "deadline" in obj.__dict__

    def __call__(self):
        query = {'portal_type': 'opengever.task.task'}
        for obj in self.objects(query, "Persist deadline on tasks"):
            if self.is_deadline_persisted(obj):
                continue

            ITask(obj).deadline = obj.get_sql_object().deadline
            obj.reindexObject(idxs=["deadline"])
