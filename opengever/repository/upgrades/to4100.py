from ftw.upgrade import UpgradeStep


class RevokeListFolderContentsPermissoin(UpgradeStep):
    """Disable List folder contents permission for Administrators
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.repository.upgrades:4100')

        self.update_workflow_security(
            ['opengever_repository_workflow',
             'opengever_repositoryroot_workflow'],
            reindex_security=False)
