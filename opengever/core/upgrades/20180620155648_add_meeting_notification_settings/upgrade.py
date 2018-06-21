from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.activity.roles import PROPOSAL_ISSUER_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


DEFAULT_SETTINGS = [
    {'kind': 'proposal-transition-submit',
     'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]},

    {'kind': 'proposal-transition-reject',
     'badge_notification_roles': [PROPOSAL_ISSUER_ROLE]},

    {'kind': 'proposal-transition-schedule',
     'badge_notification_roles': [PROPOSAL_ISSUER_ROLE]},

    {'kind': 'proposal-transition-decide',
     'badge_notification_roles': [PROPOSAL_ISSUER_ROLE]},

    {'kind': 'proposal-commented',
     'badge_notification_roles': [PROPOSAL_ISSUER_ROLE,
                                  COMMITTEE_RESPONSIBLE_ROLE]},

    {'kind': 'proposal-attachment-updated',
     'badge_notification_roles': [PROPOSAL_ISSUER_ROLE]},

    {'kind': 'proposal-additional-documents-submitted',
     'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]},
]


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"))


class AddMeetingNotificationSettings(SchemaMigration):
    """Add meeting notification settings.
    """

    def migrate(self):
        self.insert_notification_defaults()

    def insert_notification_defaults(self):
        seq = Sequence('notification_defaults_id_seq')
        for item in DEFAULT_SETTINGS:
            setting = self.execute(defaults_table
                                   .select()
                                   .where(defaults_table.columns.kind == item.get('kind')))

            if setting.rowcount:
                # We don't want to reset already inserted settings
                continue

            self.execute(defaults_table
                         .insert()
                         .values(id=self.execute(seq),
                                 kind=item['kind'],
                                 badge_notification_roles=json.dumps(item['badge_notification_roles'])))
