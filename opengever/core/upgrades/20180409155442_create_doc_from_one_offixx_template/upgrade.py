from ftw.upgrade import UpgradeStep


class CreateDocFromOneOffixxTemplate(UpgradeStep):
    """Create doc from one offixx template.
    """

    def __call__(self):
        self.install_upgrade_profile()
