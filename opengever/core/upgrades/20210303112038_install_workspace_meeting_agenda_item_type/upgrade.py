from ftw.upgrade import UpgradeStep


class InstallWorkspaceMeetingAgendaItemType(UpgradeStep):
    """Install workspace meeting agenda item type.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_workspace'],
                                      reindex_security=False)
