from ftw.upgrade import UpgradeStep


class MoveBaseJavascriptAfterKeywordwidget(UpgradeStep):
    """Move base javascript after keywordwidget.
    """

    def __call__(self):
        self.install_upgrade_profile()
