from ftw.upgrade import UpgradeStep


class ProvideActionToCreateForwardingOnDocument(UpgradeStep):
    """Provide action to create forwarding on document.
    """

    def __call__(self):
        self.install_upgrade_profile()
