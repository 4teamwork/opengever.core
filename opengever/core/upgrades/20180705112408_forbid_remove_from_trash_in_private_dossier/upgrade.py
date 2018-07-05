from ftw.upgrade import UpgradeStep


class ForbidRemoveFromTrashInPrivateDossier(UpgradeStep):
    """Forbid remove from trash in private dossier.
    """

    def __call__(self):
        self.install_upgrade_profile()
