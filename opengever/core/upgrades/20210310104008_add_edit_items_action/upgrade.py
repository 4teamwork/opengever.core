from ftw.upgrade import UpgradeStep


class AddEditItemsAction(UpgradeStep):
    """Add edit_items action.
    """

    def __call__(self):
        self.install_upgrade_profile()
