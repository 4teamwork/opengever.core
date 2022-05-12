from ftw.upgrade import UpgradeStep


class AddOnlyAttachOriginalIfConversionIsMissingFlag(UpgradeStep):
    """Add only attach original if conversion is missing flag.
    """

    def __call__(self):
        self.install_upgrade_profile()
