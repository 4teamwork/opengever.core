from ftw.upgrade import UpgradeStep


class ManageCheckinCheckoutPermissionsInSubmittedProposal(UpgradeStep):
    """Manage checkin/checkout permissions in submitted proposal.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(
            ['opengever_submitted_proposal_workflow'], reindex_security=False)
