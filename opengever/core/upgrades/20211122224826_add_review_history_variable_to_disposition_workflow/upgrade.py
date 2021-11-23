from ftw.upgrade import UpgradeStep


class AddReviewHistoryVariableToDispositionWorkflow(UpgradeStep):
    """Add review_history variable to disposition workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
