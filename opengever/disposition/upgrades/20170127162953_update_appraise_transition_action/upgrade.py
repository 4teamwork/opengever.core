from ftw.upgrade import UpgradeStep


class UpdateAppraiseTransitionAction(UpgradeStep):
    """Update appraise transition action.
    """

    def __call__(self):
        self.install_upgrade_profile()
