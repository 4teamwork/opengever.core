from ftw.upgrade import UpgradeStep


class AddWaitingPeriodSourceFileRemovalConfiguration(UpgradeStep):
    """Add waiting_period source_file removal configuration.
    """

    def __call__(self):
        self.install_upgrade_profile()
