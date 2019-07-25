from ftw.upgrade import UpgradeStep


class AddNumberingAndNamingBehaviorsToToDos(UpgradeStep):
    """Add numbering and naming behaviors to ToDos.
    """

    def __call__(self):
        self.install_upgrade_profile()
