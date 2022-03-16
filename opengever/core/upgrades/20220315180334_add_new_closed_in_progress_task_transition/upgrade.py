from ftw.upgrade import UpgradeStep


class AddNewClosedInProgressTaskTransition(UpgradeStep):
    """Add new closed-in-progress task transition.
    """

    def __call__(self):
        self.install_upgrade_profile()
