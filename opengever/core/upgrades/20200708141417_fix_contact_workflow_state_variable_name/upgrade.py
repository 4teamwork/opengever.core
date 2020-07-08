from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
import logging


logger = logging.getLogger('ftw.upgrade')

WORKFLOW_TO_MIGRATE = 'opengever_contact_workflow'


class FixContactWorkflowStateVariableName(UpgradeStep):
    """Fix contact workflow state variable name.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'portal_type': 'opengever.contact.contact'}
        for contact in self.objects(query, 'Migrate contacts'):
            self.migrate_contact_workflow_history(contact)
            contact.reindexObject(idxs=['review_state'])

    def migrate_contact_workflow_history(self, contact):
        contact = aq_base(contact)  # unwrap
        if not hasattr(contact, 'workflow_history'):
            logger.warning('no workflow history for {}'.format(
                '/'.join(contact.getPhysicalPath())))
            return

        workflow_history = contact.workflow_history
        if WORKFLOW_TO_MIGRATE not in workflow_history:
            logger.warning('no workflow entries for {}'.format(
                '/'.join(contact.getPhysicalPath())))
            return

        workflow_history[WORKFLOW_TO_MIGRATE] = map(
            self.migrate_contact_workflow_entry_state_var_name,
            workflow_history[WORKFLOW_TO_MIGRATE]
        )

    def migrate_contact_workflow_entry_state_var_name(self, entry):
        entry = entry.copy()
        state = entry.pop('state', None)
        if state:
            entry['review_state'] = state
        return entry
