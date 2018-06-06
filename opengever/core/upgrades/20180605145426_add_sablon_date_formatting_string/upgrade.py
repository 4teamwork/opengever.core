from ftw.upgrade import UpgradeStep


class AddSablonDateFormattingString(UpgradeStep):
    """Add sablon date formatting string.
    """

    def __call__(self):
        self.install_upgrade_profile()
