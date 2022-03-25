from ftw.upgrade import UpgradeStep


class AllowNestingTaskTemplateFolders(UpgradeStep):
    """Allow nesting task template folders.
    """

    def __call__(self):
        self.install_upgrade_profile()
