from ftw.upgrade import UpgradeStep


class AddSubmittedProposalWorkflow(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-opengever.meeting.upgrades:4300')

        self.update_workflow_security(
            ['opengever_submitted_proposal_workflow'], reindex_security=False)
