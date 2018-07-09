from opengever.activity.model import NotificationDefault
from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.core.upgrade import SchemaMigration


class FixProposalActivitySettingsDefaults(SchemaMigration):
    """Fix proposal activity settings defaults.
    """

    def migrate(self):
        setting = NotificationDefault.query.filter(
            NotificationDefault.kind == 'proposal-attachment-updated').first()

        setting.badge_notification_roles = [COMMITTEE_RESPONSIBLE_ROLE]
