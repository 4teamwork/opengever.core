from ftw.upgrade import UpgradeStep


class ChangeToOriginalPloneFormwidgetAutocomplete(UpgradeStep):
    """Change to original plone.formwidget.autocomplete.
    """

    def __call__(self):
        self.setup_install_profile(
            'profile-plone.formwidget.autocomplete:default')
        self.install_upgrade_profile()
