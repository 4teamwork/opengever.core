from ftw.upgrade import UpgradeStep


class EnableFtwKeywordwidgetAndIndexKeywordsOfDossiers(UpgradeStep):
    """Enable ftw.keywordwidget and index keywords of Dossiers.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.keywordwidget:default')
        self.setup_install_profile('profile-ftw.keywordwidget:select2js')
        self.install_upgrade_profile()
