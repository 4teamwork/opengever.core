from ftw.upgrade import UpgradeStep


class AllowCopyOrMoveForClosedDossierStates(UpgradeStep):
    """Dossier Workflows: Allow 'Copy or Move' for Dossier in closed states
    (resolved and inactive).
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.dossier.upgrades:4501')

        self.update_workflow_security(['opengever_dossier_workflow'],
                                      reindex_security=False)
