from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class AddDefaultSettingsTable(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4300

    def migrate(self):
        self.add_notification_defaults_table()

    def add_notification_defaults_table(self):
        self.op.create_table(
            'notification_defaults',
            Column("id", Integer, primary_key=True),
            Column("kind", String(50), nullable=False, unique=True),
            Column("mail_notification", Boolean, nullable=False, default=False)
        )
