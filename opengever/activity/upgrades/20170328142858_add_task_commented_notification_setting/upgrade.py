from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


DEFAULT_SETTINGS = [
    {'kind': 'task-commented',
     'mail_notification': False,
     'mail_notification_roles': []}
]


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("mail_notification"),
    column("mail_notification_roles"))


class AddTaskCommentedNotificationSetting(SchemaMigration):
    """Add task commented notification setting.
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

            values = dict(kind=item['kind'],
                          mail_notification=item['mail_notification'],
                          mail_notification_roles=json.dumps(
                              item['mail_notification_roles']))
            if self.supports_sequences:
                values['id'] = self.execute(seq)

            self.execute(defaults_table.insert().values(**values))
