from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ftw.upgrade.placefulworkflow import PlacefulWorkflowPolicyActivator
from ftw.upgrade.utils import SizedGenerator
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from opengever.inbox.container import IInboxContainer
from opengever.inbox.inbox import IInbox
from plone import api
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
import itertools
import logging


logger = logging.getLogger('ftw.upgrade')

POLICY_ID = "opengever_inbox_policy"

REVIEW_STATE_MAPPING = {
    ('opengever_mail_workflow', 'opengever_inbox_mail_workflow'): {
        'mail-state-active': 'mail-state-active',
        'mail-state-removed': 'mail-state-removed',
    },
    ('opengever_document_workflow', 'opengever_inbox_document_workflow'): {
        'document-state-draft': 'document-state-draft',
        'document-state-removed': 'document-state-removed',
        'document-state-shadow': 'document-state-shadow',
    },
}

WORKFLOW_NAMES = list(itertools.chain(*REVIEW_STATE_MAPPING.keys()))


class InboxWorkflowSecurityUpdater(WorkflowSecurityUpdater):

    def __init__(self, inbox):
        self.inbox = inbox

    def lookup_objects(self, types):
        catalog = api.portal.get_tool('portal_catalog')
        query = {
            'portal_type': types,
            'path': {
                'query': '/'.join(self.inbox.getPhysicalPath()),
                'depth': -1,
            },
        }
        brains = tuple(catalog.unrestrictedSearchResults(query))
        generator = SizedGenerator(
            (brain._unrestrictedGetObject() for brain in brains), len(brains))
        return ProgressLogger('Update object security', generator)


class FixInboxWorkflowPolicyAssignment(UpgradeStep):
    """Fix inbox workflow policy assignment.
    """

    deferrable = True

    def __call__(self):
        self.pwf_tool = api.portal.get_tool('portal_placeful_workflow')

        container_query = {
            'object_provides': [IInboxContainer.__identifier__]
        }
        containers = self.catalog_unrestricted_search(
            container_query, full_objects=True
        )
        if containers:
            self.fix_inboxes_in_container(containers)
        else:
            self.fix_global_inbox()

    def fix_inboxes_in_container(self, containers):
        for container in containers:
            container_path = '/'.join(container.getPhysicalPath())
            query = {
                'path': {'query': container_path, 'depth': 1},
                'object_provides': [IInbox.__identifier__]
            }

            inboxes = self.catalog_unrestricted_search(
                query, full_objects=True
            )

            config = self.pwf_tool.getWorkflowPolicyConfig(container)
            has_container_workflow = False
            if config:
                has_container_workflow = (
                    config.getPolicyInId() == POLICY_ID
                    and config.getPolicyBelowId() == POLICY_ID
                )
                # drop placeful workflow config from container
                container._delObject(WorkflowPolicyConfig_id)

            for inbox in inboxes:
                self.fix_inbox(
                    inbox, has_container_workflow=has_container_workflow
                )

    def fix_global_inbox(self):
        query = {
            'object_provides': [IInbox.__identifier__]
        }
        inboxes = self.catalog_unrestricted_search(
            query, full_objects=True
        )
        if len(inboxes) > 1:
            logger.warning('Multiple global inboxes found.')

        for inbox in inboxes:
            self.fix_inbox(inbox, has_container_workflow=False)

    def fix_inbox(self, inbox, has_container_workflow=False):
        has_inbox_workflow = False
        config = self.pwf_tool.getWorkflowPolicyConfig(inbox)
        if config:
            has_inbox_workflow = (
                config.getPolicyInId() == POLICY_ID
                and config.getPolicyBelowId() == POLICY_ID
            )
        if has_inbox_workflow:
            # we already have a placeful workflow on the inbox, nothing to do
            return

        if has_container_workflow:
            # we previously had the placeful workflow from the inbox container
            # we just activate it for the inbox but do not need to update any
            # document/mail workflows
            if not config:
                inbox.manage_addProduct[
                    'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
                config = self.pwf_tool.getWorkflowPolicyConfig(inbox)
            config.setPolicyIn(POLICY_ID, update_security=False)
            config.setPolicyBelow(POLICY_ID, update_security=False)
        else:
            # we did not have the placeful placeful workflow on the inbox and
            # we did not inherit it from the inbox container
            activator = PlacefulWorkflowPolicyActivator(inbox)
            activator.activate_policy(
                POLICY_ID,
                review_state_mapping=REVIEW_STATE_MAPPING,
                update_security=False,
            )

            # manually update security in inboxes to avoid touching all
            # documents
            updater = InboxWorkflowSecurityUpdater(inbox)
            updater.update(
                WORKFLOW_NAMES,
                reindex_security=False,
                savepoints=1000,
            )
