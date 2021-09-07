from ftw.upgrade import UpgradeStep


class ReindexAcceptedTeamTasksResponsible(UpgradeStep):
    """Reindex accepted team tasks responsible.
    """

    deferrable = True

    def __call__(self):
        catalog = self.getToolByName('portal_catalog')
        query = {'object_provides': 'opengever.task.task.ITask',
                 'review_state': 'task-state-in-progress'}

        for task in self.brains(query, "Reindex accepted team tasks responsible."):
            catalog_data = catalog.getIndexDataForRID(task.getRID())
            responsible = catalog_data.get('responsible')
            if responsible and responsible.startswith("team:"):
                task.getObject().reindexObject(idxs=["responsible"])
