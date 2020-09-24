from AccessControl.ImplPython import name_trans
from Acquisition import aq_base
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for
from ftw.upgrade.utils import SavepointIterator
from ftw.upgrade.utils import SizedGenerator
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
import string


def permission_attribute_name(permission):
    """The attribute name used to store the permission on the object."""
    return '_' + string.translate(permission, name_trans) + "_Permission"


def delete_unmanaged_permission_attributes(obj):
    """Delete permissions stored on the object that are not managed by the
       objects workflow.
    """
    wftool = getToolByName(getSite(), 'portal_workflow')
    wf_permissions = [
        permission_attribute_name(p) for p
        in wftool.getWorkflowsFor(obj)[0].permissions
    ]
    obj_permissions = [p for p in dir(aq_base(obj)) if p.endswith('_Permission')]
    for permission in obj_permissions:
        if permission not in wf_permissions:
            delattr(obj, permission)


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
        generator = SizedGenerator(
            (brain._unrestrictedGetObject() for brain in brains), len(brains))
        return ProgressLogger('Update object security', generator)

    # Additionally deletes permissions stored on the object
    def update(self, changed_workflows, reindex_security=True, savepoints=None):
        types = self.get_suspected_types(changed_workflows)
        objects = SavepointIterator.build(self.lookup_objects(types), savepoints)
        for obj in objects:
            if self.obj_has_workflow(obj, changed_workflows):
                update_security_for(obj, reindex_security=reindex_security)
                delete_unmanaged_permission_attributes(obj)


class FixWorkspaceWorkflows(UpgradeStep):
    """Fix workspace workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            [
                'opengever_workspace_folder',
                'opengever_workspace_document',
            ],
            reindex_security=False, savepoints=None
        )

    def update_workflow_security(self, workflow_names, reindex_security=True,
                                 savepoints=1000):
        updater = WorkflowSecurityUpdater()
        updater.update(workflow_names, reindex_security=reindex_security,
                       savepoints=savepoints)
