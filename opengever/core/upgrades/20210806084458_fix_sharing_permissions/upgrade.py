from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for
from ftw.upgrade.utils import SavepointIterator
from ftw.upgrade.utils import SizedGenerator
from plone import api
from zope.component.hooks import getSite


class FixSharingPermissions(UpgradeStep):
    """Fix sharing permissions.
    """

    deferrable = True

    def __call__(self):
        self.catalog = api.portal.get_tool('portal_catalog')
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_tasktemplatefolder_workflow',
             'opengever_inbox_workflow',
             'opengever_disposition_workflow',
             'opengever_proposal_workflow'],
            reindex_security=False)

        # We can't use the update_workflow_security for inbox and private
        # documents otherwise we would update also all regular documents
        # therefore we fetch and updated them manually
        inbox_path = self.get_inbox_path()
        if inbox_path:
            self.update_workflow_for_documents(inbox_path)

        private_path = self.get_private_path()
        if private_path:
            self.update_workflow_for_documents(private_path)

    def update_workflow_for_documents(self, path):
        # Copied from ftw.upgrade.workflow.WorkflowSecurityUpdater
        portal = getSite()
        query = {'portal_type': 'opengever.document.document', 'path': path}
        brains = tuple(self.catalog.unrestrictedSearchResults(query))
        lookup = lambda brain: portal.unrestrictedTraverse(brain.getPath())
        generator = SizedGenerator(
            (lookup(brain) for brain in brains), len(brains))
        objects = SavepointIterator.build(
            ProgressLogger('Update object security', generator), 1000)

        for obj in objects:
            update_security_for(obj, reindex_security=False)

    def get_inbox_path(self):
        containers = self.catalog.unrestrictedSearchResults(
            portal_type='opengever.inbox.container')
        if len(containers):
            return containers[0].getPath()

        inboxes = self.catalog.unrestrictedSearchResults(
            portal_type='opengever.inbox.inbox')
        if len(inboxes):
            return inboxes[0].getPath()

    def get_private_path(self):
        roots = self.catalog.unrestrictedSearchResults(
            portal_type='opengever.private.root')
        if len(roots):
            return roots[0].getPath()
