from ftw.upgrade import UpgradeStep
from ftw.upgrade.placefulworkflow import PlacefulWorkflowPolicyActivator
from opengever.inbox.container import IInboxContainer
from opengever.inbox.inbox import IInbox
from plone import api


class AddPlacefulWorkflowForInboxArea(UpgradeStep):
    """Add placeful workflow for inbox area.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_inbox_workflow()

    def update_inbox_workflow(self):
        self.update_workflow_security(
            ['opengever_inbox_workflow'],
            reindex_security=False)

        inboxes = api.content.find(
            context=api.portal.get(),
            depth=1,
            object_provides=[IInbox, IInboxContainer])

        for brain in inboxes:
            inbox = brain.getObject()

            activator = PlacefulWorkflowPolicyActivator(inbox)
            activator.activate_policy(
                'opengever_inbox_policy',
                review_state_mapping={
                    ('opengever_document_workflow',
                     'opengever_inbox_document_workflow'): {
                         'document-state-draft': 'document-state-draft',
                         'document-state-removed': 'document-state-removed',
                         'document-state-shadow': 'document-state-shadow'}})
