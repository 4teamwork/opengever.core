from ftw.upgrade import UpgradeStep


class AdjustRepositoryPermissions(UpgradeStep):
    """Adjust permission for repository and repositoryroot objects:
     - Disable `List folder contents` permission for Administrators.
     - No longer aqcuire `Delete objects` permission and give to
    Administrators and Managers
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4100')

        self.update_workflow_security(
            ['opengever_repository_workflow',
             'opengever_repositoryroot_workflow'],
            reindex_security=False)
