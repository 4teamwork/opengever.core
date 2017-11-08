from ftw.upgrade import UpgradeStep


class AllowToDeleteContentsOfPrivateFolder(UpgradeStep):
    """Allow to delete contents of private folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_private_folder_workflow',
                                       'opengever_private_dossier_workflow'],
                                      reindex_security=False)
