from ftw.upgrade import UpgradeStep


class AddMetadataBehaviorToDocumentFTI(UpgradeStep):
    """Add the IDocumentMetadata behavior to the og.document.document FTI.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.document.upgrades:3402')
