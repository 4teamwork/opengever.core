from ftw.upgrade import UpgradeStep
from opengever.quota.sizequota import ISizeQuota


class FixPrivateFolderUsageCalculation(UpgradeStep):
    """Fix private folder usage calculation.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.calculate_private_folder_usage()

    def calculate_private_folder_usage(self):
        msg = 'Calculate usage in private folders.'
        for obj in self.objects({'portal_type': ['opengever.private.folder']},
                                msg):
            ISizeQuota(obj).recalculate()
