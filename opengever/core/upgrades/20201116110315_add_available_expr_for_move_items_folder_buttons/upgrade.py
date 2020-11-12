from ftw.upgrade import UpgradeStep


class AddAvailableExprForMoveItemsFolderButtons(UpgradeStep):
    """Add available expr for move items folder buttons.
    """

    def __call__(self):
        self.install_upgrade_profile()
