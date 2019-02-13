from ftw.upgrade import UpgradeStep


class DropTheListOfOfficeConnectorEditableMIMETypesFromTheRegistry(UpgradeStep):
    """Drop the list of office connector editable MIME types from the registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
