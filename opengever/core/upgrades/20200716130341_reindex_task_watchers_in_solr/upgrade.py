from ftw.upgrade import UpgradeStep
from opengever.task.task import ITask


class ReindexTaskWatchersInSolr(UpgradeStep):
    """Reindex task watchers in solr.
    """

    deferrable = True

    def __call__(self):
        query = {'object_provides': ITask.__identifier__}
        for task in self.objects(query, 'Reindex task watchers.'):
            # watchers is only in solr, prevent reindexing all catalog indexes
            # by picking a cheap catalog index `UID`.
            task.reindexObject(idxs=['UID', 'watchers'])
