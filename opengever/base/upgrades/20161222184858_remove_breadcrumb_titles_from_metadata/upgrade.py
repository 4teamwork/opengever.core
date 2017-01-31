from ftw.upgrade import UpgradeStep


class RemoveBreadcrumbTitlesFromMetadata(UpgradeStep):
    """Remove breadcrumb_titles from metadata.
    """

    def __call__(self):
        self.install_upgrade_profile()
