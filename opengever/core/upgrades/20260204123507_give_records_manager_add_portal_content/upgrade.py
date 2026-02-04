from ftw.upgrade import UpgradeStep


class GiveRecordsManagerAddPortalContent(UpgradeStep):
    """Give Records Manager the add portal content permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
