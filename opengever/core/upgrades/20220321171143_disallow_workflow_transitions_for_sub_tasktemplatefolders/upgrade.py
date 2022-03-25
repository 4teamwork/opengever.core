from ftw.upgrade import UpgradeStep


class DisallowWorkflowTransitionsForSubTasktemplatefolders(UpgradeStep):
    """Disallow workflow transitions for sub tasktemplatefolders.
    """

    def __call__(self):
        self.install_upgrade_profile()
