from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


TASK_ISSUER_ROLE = 'task_issuer'
TASK_RESPONSIBLE_ROLE = 'task_responsible'


class AddMissingForwardingAddedNotificationDefault(SchemaMigration):
    """Add missing forwarding-added notification_default.
    """

    defaults_table = table(
        "notification_defaults",
        column("id"),
        column("kind"),
        column("mail_notification_roles"),
        column("badge_notification_roles")
    )

    def migrate(self):
        query = self.defaults_table.select().where(
            self.defaults_table.c.kind == 'forwarding-added')
        forwarding_added = self.connection.execute(query).fetchall()

        if not len(forwarding_added):
            self.insert_forwarding_added_default()

    def insert_forwarding_added_default(self):
        values = {
            'kind': 'forwarding-added',
            'mail_notification_roles': json.dumps([TASK_RESPONSIBLE_ROLE]),
            'badge_notification_roles': json.dumps(
                [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE])}

        seq = Sequence('notification_defaults_id_seq')
        if self.supports_sequences:
            values['id'] = self.execute(seq)

        self.execute(self.defaults_table.insert().values(**values))
