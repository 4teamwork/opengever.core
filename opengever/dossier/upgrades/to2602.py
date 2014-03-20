from ftw.upgrade import UpgradeStep


class UpdateFtwMail(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.dossier.upgrades:2602')

        self.update_workflow_security(['opengever_dossier_workflow'],
                                      reindex_security=True)
