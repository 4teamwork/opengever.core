from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask


class ReindexTaskPrincipalsInGlobalindex(UpgradeStep):
    """Reindex task principals in globalindex.
    """

    def __call__(self):
        query = {'object_provides': ITask.__identifier__}
        for task in self.objects(query, 'Reindex task principals'):
            sql_task = task.get_sql_object()
            sql_task.principals = task.get_principals()
