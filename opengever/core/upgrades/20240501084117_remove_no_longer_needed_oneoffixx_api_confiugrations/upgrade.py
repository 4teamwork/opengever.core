from ftw.upgrade import UpgradeStep


class RemoveNoLongerNeededOneoffixxApiConfiugrations(UpgradeStep):
    """Remove no longer needed oneoffixx api confiugrations.
    """

    def __call__(self):
        self.install_upgrade_profile()
