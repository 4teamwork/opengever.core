from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


TASK_RESPONSIBLE_ROLE = 'task_responsible'
DEFAULT_SETTINGS = {
    'task-added': [TASK_RESPONSIBLE_ROLE],
    'task-transition-reassign': [TASK_RESPONSIBLE_ROLE],
    'forwarding-transition-reassign-refused': [TASK_RESPONSIBLE_ROLE]
}


class AddRolesColumn(SchemaMigration):
    """Add new column mail_notification_roles column to the NotificationDefault
    table. Add default settings.

    This is introcued during Release 4.6. development, but will be
    backported to 4.5 Release.
    """

    profileid = 'opengever.activity'
    upgradeid = 4502

    def migrate(self):
        self.add_roles_column()
        self.insert_notification_defaults()

    def add_roles_column(self):
        self.op.add_column('notification_defaults',
                           Column('mail_notification_roles', Text))

    def insert_notification_defaults(self):
        defaults_table = table(
            "notification_defaults",
            column("id"),
            column("kind"),
            column("mail_notification_roles"),
        )

        settings = self.connection.execute(defaults_table.select()).fetchall()
        for setting in settings:
            roles = DEFAULT_SETTINGS.get(setting.kind)
            if not roles:
                continue

            self.execute(
                defaults_table.update()
                .values(mail_notification_roles=json.dumps(roles))
                .where(defaults_table.columns.id == setting.id)
            )
