from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyWorkflowSecurityUpdater


class AddLimitedAdminRole(UpgradeStep):
    """Add LimitedAdmin role.
    """

    deferrable = False

    def __call__(self):
        self.install_upgrade_profile()
        with NightlyWorkflowSecurityUpdater(reindex_security=True) as updater:
            updater.update(
                ['opengever_contact_workflow',
                 'opengever_contactfolder_workflow',
                 'opengever_document_workflow',
                 'opengever_dossier_workflow',
                 'opengever_forwarding_workflow',
                 'opengever_inbox_document_workflow',
                 'opengever_inbox_mail_workflow',
                 'opengever_inbox_workflow',
                 'opengever_mail_workflow',
                 'opengever_meetingtemplate_workflow',
                 'opengever_paragraphtemplate_workflow',
                 'opengever_proposal_workflow',
                 'opengever_repository_workflow',
                 'opengever_repositoryroot_workflow',
                 'opengever_submitted_proposal_workflow',
                 'opengever_task_workflow',
                 'opengever_tasktemplate_workflow',
                 'opengever_tasktemplatefolder_workflow',
                 'opengever_templatefolder_workflow'])
