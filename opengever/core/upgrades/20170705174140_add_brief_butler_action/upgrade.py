from ftw.upgrade import UpgradeStep


class AddBriefButlerAction(UpgradeStep):
    """add BriefButler action.
    """

    def __call__(self):
        self.install_upgrade_profile()
