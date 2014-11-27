from ftw.upgrade import UpgradeStep


class RevokeDeletePermissions(UpgradeStep):
    """Revoke delete permissions for dossiers, because the Administrator role
    has newly the `Delete objects` permission on repositories.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.dossier.upgrades:4100')

        self.update_workflow_security(['opengever_dossier_workflow'],
                                      reindex_security=False)
