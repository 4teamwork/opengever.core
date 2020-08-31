from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ftw.upgrade.utils import SizedGenerator
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


class WorkflowSecurityUpdater(WorkflowSecurityUpdater):
    # Customized WorkflowSecurityUpdater that only updates object inside a
    # workspace root. We want to avoid updating all GEVER documents as the
    # workflow changes only affect workspaces.
    def lookup_objects(self, types):
        portal = getSite()
        catalog = getToolByName(portal, 'portal_catalog')

        workspace_roots = catalog.unrestrictedSearchResults(
            portal_type='opengever.workspace.root')
        query = {
            'portal_type': types,
            'path': {
                'query': [root.getPath() for root in workspace_roots],
                'depth': -1,
            },
        }
        brains = tuple(catalog.unrestrictedSearchResults(query))
        lookup = lambda brain: portal.unrestrictedTraverse(brain.getPath())
        generator = SizedGenerator((lookup(brain) for brain in brains),
                                   len(brains))
        return ProgressLogger('Update object security', generator)


class UpdateWorkspaceWorkflow(UpgradeStep):
    """Update workspace workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            [
                'opengever_workspace',
                'opengever_workspace_folder',
                'opengever_workspace_todolist',
                'opengever_workspace_todo',
                'opengever_document_workflow',
            ],
            reindex_security=False, savepoints=None
        )

    def update_workflow_security(self, workflow_names, reindex_security=True,
                                 savepoints=1000):
        updater = WorkflowSecurityUpdater()
        updater.update(workflow_names, reindex_security=reindex_security,
                       savepoints=savepoints)
