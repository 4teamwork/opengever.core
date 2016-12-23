from ftw.upgrade import UpgradeStep


class RemoveJSExpresion(UpgradeStep):
    """Remove js expresion.
    """

    def __call__(self):
        self.install_upgrade_profile()
