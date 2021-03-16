from ftw.upgrade import UpgradeStep


class RemoveWorkspaceAgendaitemFromSearch(UpgradeStep):
    """Remove workspace agendaitem from search.
    """

    def __call__(self):
        self.install_upgrade_profile()
