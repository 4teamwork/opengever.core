from ftw.upgrade import UpgradeStep


class AddOpenXMLVisioDrawingsToOfficeconnectorEditableTypes(UpgradeStep):
    """Add Open XML Visio Drawings to officeconnector editable types.
    """

    def __call__(self):
        self.install_upgrade_profile()
