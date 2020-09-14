from ftw.upgrade import UpgradeStep


class AddMoveItemAction(UpgradeStep):
    """Add move_item action.
    """

    def __call__(self):
        self.install_upgrade_profile()
