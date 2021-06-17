from ftw.upgrade import UpgradeStep


class AllowToReassignTasksInAllNonFinalStates(UpgradeStep):
    """Allow to reassign tasks in all non final states.
    """

    def __call__(self):
        self.install_upgrade_profile()
