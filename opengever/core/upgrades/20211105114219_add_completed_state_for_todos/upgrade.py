from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from plone import api


class AddCompletedStateForTodos(UpgradeStep):
    """Add completed state for todos.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'portal_type': 'opengever.workspace.todo'}
        for obj in ProgressLogger('Migrate completed field',
                                  self.catalog_unrestricted_search(query, full_objects=True)):
            if obj.completed:
                api.content.transition(
                    obj=obj,
                    transition='opengever_workspace_todo--TRANSITION--complete--active_completed')
