from ftw.upgrade import UpgradeStep


class InstallFtwTokenauth(UpgradeStep):
    """Install ftw.tokenauth.

    This installs the ftw.tokenauth:default profile, which sets up the
    PAS plugin in acl_users/token_auth and registers the "Manage Service Keys"
    action.

    Mapping the "ftw.tokenauth: Manage own Service Keys" permission to a
    role needs to be done separately.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.tokenauth:default')
