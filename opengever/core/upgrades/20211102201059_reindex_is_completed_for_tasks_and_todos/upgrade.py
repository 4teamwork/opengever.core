from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from opengever.task.task import ITask
from opengever.workspace.interfaces import IToDo


class ReindexIsCompletedForTasksAndTodos(UpgradeStep):
    """Reindex is_completed for tasks and todos.
    """

    deferrable = True

    def __call__(self):
        self.index_is_completed()

    def index_is_completed(self):
        query = {
            'object_provides': [ITask.__identifier__, IToDo.__identifier__]}

        with NightlyIndexer(idxs=["is_completed"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index is_completed in Solr'):
                indexer.add_by_brain(brain)
