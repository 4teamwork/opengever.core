from ftw.upgrade import UpgradeStep


class UninstallTreeview(UpgradeStep):

    def __call__(self):
        quickinstaller = self.getToolByName('portal_quickinstaller')
        quickinstaller.uninstallProducts(['ftw.treeview'])
