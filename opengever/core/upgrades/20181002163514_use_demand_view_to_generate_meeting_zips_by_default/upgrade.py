from ftw.upgrade import UpgradeStep


class UseDemandViewToGenerateMeetingZipsByDefault(UpgradeStep):
    """Use demand view to generate meeting zips by default.
    """

    def __call__(self):
        self.install_upgrade_profile()
