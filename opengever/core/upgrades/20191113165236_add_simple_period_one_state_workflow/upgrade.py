from ftw.upgrade import UpgradeStep


class AddSimplePeriodOneStateWorkflow(UpgradeStep):
    """Add simple period one-state workflow.
    """

    def __call__(self):
        self.install_upgrade_profile()
