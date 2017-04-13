from ftw.upgrade import UpgradeStep


class DonTShowPdfActionsOnPrivateDossier(UpgradeStep):
    """Don't show pdf actions on private dossier.
    """

    def __call__(self):
        self.install_upgrade_profile()
