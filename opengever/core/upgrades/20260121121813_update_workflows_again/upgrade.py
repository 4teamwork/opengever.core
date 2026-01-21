from ftw.upgrade import UpgradeStep


class UpdateWorkflowsAgain(UpgradeStep):
    """Update workflows again.
    """

    def __call__(self):
        self.install_upgrade_profile()
