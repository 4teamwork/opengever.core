from ftw.upgrade import UpgradeStep


class AddCreateTaskFromProposalAction(UpgradeStep):
    """Add create_task_from_proposal action.
    """

    def __call__(self):
        self.install_upgrade_profile()
