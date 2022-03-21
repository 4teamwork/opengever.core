from ftw.upgrade import UpgradeStep


class FixPrivateMailWorkflow(UpgradeStep):
    """Fix private mail workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
