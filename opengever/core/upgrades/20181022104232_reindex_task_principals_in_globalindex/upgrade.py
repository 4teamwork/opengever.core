from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask
import logging

logger = logging.getLogger('opengever.core')


class ReindexTaskPrincipalsInGlobalindex(UpgradeStep):
    """Reindex task principals in globalindex.
    """

    def __call__(self):
        query = {'object_provides': ITask.__identifier__}
        for task in self.objects(query, 'Reindex task principals'):
            sql_task = task.get_sql_object()
            if not sql_task:
                logger.warning(u'Reindexing of task {} has been skipped, SQL '
                               u'representation is missing'.format(task))
                continue

            sql_task.principals = task.get_principals()
