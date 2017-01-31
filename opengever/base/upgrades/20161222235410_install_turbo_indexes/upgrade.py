from ftw.upgrade import UpgradeStep
from opengever.base.hooks import replace_with_turbo_index
from opengever.base.indexes import UserTurboIndex


class InstallTurboIndexes(UpgradeStep):
    """Install turbo indexes.
    """

    def __call__(self):
        self.install_upgrade_profile()
        replace_with_turbo_index(self.portal, 'Creator', UserTurboIndex)
        replace_with_turbo_index(self.portal, 'responsible', UserTurboIndex)
