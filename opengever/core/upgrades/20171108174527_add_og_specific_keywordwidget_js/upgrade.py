from ftw.upgrade import UpgradeStep


class AddOGSpecificKeywordwidgetJS(UpgradeStep):
    """Add opengever sepcific keywordwidget.js.
    """

    def __call__(self):
        self.install_upgrade_profile()
