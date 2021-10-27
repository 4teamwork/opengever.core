from ftw.upgrade import UpgradeStep


class AddEditPublicTrialStatusAction(UpgradeStep):
    """Add edit public-trial status action.
    """

    def __call__(self):
        self.install_upgrade_profile()
