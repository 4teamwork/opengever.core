from ftw.upgrade import UpgradeStep


class AddMicrosoftPublisherToMimetypesRegistry(UpgradeStep):
    """Add microsoft publisher to mimetypes registry.
    """

    def __call__(self):
        self.install_upgrade_profile()
