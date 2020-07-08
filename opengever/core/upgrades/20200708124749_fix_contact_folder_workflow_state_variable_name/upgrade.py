from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
import logging


logger = logging.getLogger('ftw.upgrade')

WORKFLOW_TO_MIGRATE = 'opengever_contactfolder_workflow'


class FixContactFolderWorkflowStateVariableName(UpgradeStep):
    """Fix contact folder workflow state variable name.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'portal_type': 'opengever.contact.contactfolder'}
        for contactfolder in self.objects(query, 'Migrate contactfolders'):
            self.migrate_contactfolder_workflow_history(contactfolder)
            contactfolder.reindexObject(idxs=['review_state'])

    def migrate_contactfolder_workflow_history(self, contactfolder):
        contactfolder = aq_base(contactfolder)  # unwrap
        if not hasattr(contactfolder, 'workflow_history'):
            logger.warning('no workflow history for {}'.format(
                '/'.join(contactfolder.getPhysicalPath())))
            return

        workflow_history = contactfolder.workflow_history
        if WORKFLOW_TO_MIGRATE not in workflow_history:
            logger.warning('no workflow entries for {}'.format(
                '/'.join(contactfolder.getPhysicalPath())))
            return

        workflow_history[WORKFLOW_TO_MIGRATE] = map(
            self.migrate_contactfolder_workflow_entry_state_var_name,
            workflow_history[WORKFLOW_TO_MIGRATE]
        )

    def migrate_contactfolder_workflow_entry_state_var_name(self, entry):
        entry = entry.copy()
        state = entry.pop('state', None)
        if state:
            entry['review_state'] = state
        return entry
