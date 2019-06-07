from ftw.upgrade import UpgradeStep
from opengever.document.hooks import install_modifiers


class InstallCMFEditionsModifiersThatPreventJournalVersioning(UpgradeStep):
    """Install CMFEditions modifiers that prevent journal versioning.
    """

    def __call__(self):
        install_modifiers(self.portal)
