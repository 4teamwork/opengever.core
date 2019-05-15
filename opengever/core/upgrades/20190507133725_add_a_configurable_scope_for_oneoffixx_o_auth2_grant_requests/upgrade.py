from ftw.upgrade import UpgradeStep


class AddAConfigurableScopeForOneoffixxOAuth2GrantRequests(UpgradeStep):
    """Add a configurable scope for Oneoffixx OAuth2 grant requests."""

    def __call__(self):
        self.install_upgrade_profile()
