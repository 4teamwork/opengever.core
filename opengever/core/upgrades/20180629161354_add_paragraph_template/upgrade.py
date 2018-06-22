from ftw.upgrade import UpgradeStep


class AddParagraphTemplate(UpgradeStep):
    """Add paragraph template.
    """

    def __call__(self):
        self.install_upgrade_profile()
