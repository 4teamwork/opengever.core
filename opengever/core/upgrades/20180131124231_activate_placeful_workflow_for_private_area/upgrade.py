from ftw.upgrade import UpgradeStep
from ftw.upgrade.placefulworkflow import PlacefulWorkflowPolicyActivator
from plone import api


class ActivatePlacefulWorkflowForPrivateArea(UpgradeStep):
    """Activate placeful workflow for private area.
    """

    def __call__(self):
        portal = api.portal.get()
        private_root = portal.unrestrictedTraverse('private')

        activator = PlacefulWorkflowPolicyActivator(private_root)
        activator.activate_policy(
            'opengever_private_policy',
            review_state_mapping={
                ('opengever_document_workflow', 'opengever_private_document_workflow'): {
                    'document-state-draft': 'document-state-draft',
                    'document-state-shadow': 'document-state-shadow'},
                ('opengever_mail_workflow', 'opengever_private_mail_workflow'): {
                    'mail-state-active': 'mail-state-active'}})
