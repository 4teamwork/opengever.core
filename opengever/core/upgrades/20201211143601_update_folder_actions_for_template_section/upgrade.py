from ftw.upgrade import UpgradeStep


class UpdateFolderActionsForTemplateSection(UpgradeStep):
    """Update folder actions for template section.
    """

    def __call__(self):
        self.install_upgrade_profile()
