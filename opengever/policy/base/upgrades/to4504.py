from plone.app.upgrade.utils import loadMigrationProfile
from plone.app.upgrade.v43.alphas import upgradeToI18NCaseNormalizer
from ftw.upgrade import UpgradeStep


class ExecuteDelayedPloneUpgrade(UpgradeStep):
    """Redefine a patched plone upgrade step that is expensive.

    This upgrade step reindexes all ZCTextIndex fields. This step may take
    very long for customers with a lot of data. Thus we disable the default
    plone upgrade an redefine here to allow separate execution of this step.

    The plone upgrade step is monkey-patched in opengever.base.monkeypatch.
    """

    def __call__(self):
        loadMigrationProfile(self.portal_setup,
                             'profile-plone.app.upgrade.v43:to43rc1')
        upgradeToI18NCaseNormalizer(self.portal_setup)
