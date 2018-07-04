from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


DEFAULT_SETTINGS = [

    {'kind': 'task-transition-skipped-open',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},

    {'kind': 'task-transition-rejected-skipped',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},

    {'kind': 'task-transition-planned-skipped',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]}
]


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"))


class AddNewMeetingNotificationSettings(SchemaMigration):
    """Add meeting notification settings for transitions from/to
    the new state 'skipped'.
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
