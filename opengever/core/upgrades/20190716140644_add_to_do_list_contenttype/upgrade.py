from ftw.upgrade import UpgradeStep


class AddToDoListContenttype(UpgradeStep):
    """Add ToDoList contenttype.
    """

    def __call__(self):
        self.install_upgrade_profile()
