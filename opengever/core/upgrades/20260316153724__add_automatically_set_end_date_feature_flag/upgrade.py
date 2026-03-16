from ftw.upgrade import UpgradeStep


class addAutomaticallySetEndDate(UpgradeStep):
    """Add automactically set end date feature flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
