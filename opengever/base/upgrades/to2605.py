from ftw.upgrade import UpgradeStep


class HidePasteAction(UpgradeStep):
    """Hide paste action for template dossier and contact folder"""

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.base.upgrades:2605')
