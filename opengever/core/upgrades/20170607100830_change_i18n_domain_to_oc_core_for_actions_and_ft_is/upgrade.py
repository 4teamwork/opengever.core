from ftw.upgrade import UpgradeStep


class ChangeI18nDomainToOcCoreForActionsAndFTIs(UpgradeStep):
    """Change i18n domain to oc.core for actions and FTIs.
    """

    def __call__(self):
        self.install_upgrade_profile()
