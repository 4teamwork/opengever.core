from ftw.upgrade import UpgradeStep


class HideOfferAndArchiveTransitionInActionsMenu(UpgradeStep):
    """Hide offer and archive transition in actions menu.
    """

    def __call__(self):
        self.install_upgrade_profile()
