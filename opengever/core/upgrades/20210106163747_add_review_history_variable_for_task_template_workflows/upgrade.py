from ftw.upgrade import UpgradeStep


class AddReviewHistoryVariableForTaskTemplateWorkflows(UpgradeStep):
    """Add review history variable for task template workflows.
    """

    def __call__(self):
        self.install_upgrade_profile()
