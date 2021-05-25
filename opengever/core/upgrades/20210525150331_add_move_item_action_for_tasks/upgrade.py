from ftw.upgrade import UpgradeStep


class AddMoveItemActionForTasks(UpgradeStep):
    """Add move_item action for tasks.
    """

    def __call__(self):
        self.install_upgrade_profile()
