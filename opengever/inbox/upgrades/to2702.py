from ftw.upgrade import UpgradeStep
from opengever.inbox.inbox import Inbox


class UpdateInboxTypeConfiguration(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-opengever.inbox.upgrades:2702')

        self.migrate_inbox_class()

    def migrate_inbox_class(self):
        """Remove actions of no longer used tabs"""

        for obj in self.objects({'portal_type': 'opengever.inbox.inbox'},
                                'Migrate inbox class'):

            self.migrate_class(obj, Inbox)
