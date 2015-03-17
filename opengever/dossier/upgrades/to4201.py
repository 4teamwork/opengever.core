from ftw.upgrade import UpgradeStep


class UpdateRemoveGEVERContentPermission(UpgradeStep):
    """Disable Remove GEVER content for inactive or resolved dossiers.
    """

    def __call__(self):
        self.setup_install_profile('profile-opengever.dossier.upgrades:4201')

        self.update_workflow_security(['opengever_dossier_workflow'],
                                      reindex_security=False)
