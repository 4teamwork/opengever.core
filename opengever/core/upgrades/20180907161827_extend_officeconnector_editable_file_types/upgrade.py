from ftw.upgrade import UpgradeStep


class ExtendOfficeconnectorEditableFileTypes(UpgradeStep):
    """Extend officeconnector editable file types.
    """

    def __call__(self):
        self.install_upgrade_profile()
