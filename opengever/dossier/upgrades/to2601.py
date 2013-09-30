from ftw.upgrade import UpgradeStep


class UpdateDossierReportAction(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.dossier.upgrades:2601')
