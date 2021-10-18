from ftw.upgrade import UpgradeStep


class AddInvitationMailContentSetting(UpgradeStep):
    """Add invitation_mail_content setting.
    """

    def __call__(self):
        self.install_upgrade_profile()
