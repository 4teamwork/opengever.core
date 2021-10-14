from ftw.upgrade import UpgradeStep


class EnableNightlyJobs(UpgradeStep):
    """Enable nightly jobs.
    """

    def __call__(self):
        self.install_upgrade_profile()
