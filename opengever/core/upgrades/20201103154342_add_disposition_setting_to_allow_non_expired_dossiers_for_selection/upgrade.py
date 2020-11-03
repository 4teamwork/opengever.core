from ftw.upgrade import UpgradeStep


class AddDispositionSettingToAllowNonExpiredDossiersForSelection(UpgradeStep):
    """Add disposition setting to allow non-expired dossiers for selection.
    """

    def __call__(self):
        self.install_upgrade_profile()
