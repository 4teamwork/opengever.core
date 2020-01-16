from ftw.upgrade import UpgradeStep


class AddNewTaskFromDocumentFileAction(UpgradeStep):
    """Add new_task_from_document file action.
    """

    def __call__(self):
        self.install_upgrade_profile()
