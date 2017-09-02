from ftw.upgrade import UpgradeStep


class AllowZipexportOnTemplateFolder(UpgradeStep):
    """Allow zipexport on template folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
