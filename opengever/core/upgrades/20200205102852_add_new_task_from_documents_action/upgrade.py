from ftw.upgrade import UpgradeStep


class AddNewTaskFromDocumentsAction(UpgradeStep):
    """Add new task from documents action.
    """

    def __call__(self):
        self.install_upgrade_profile()
