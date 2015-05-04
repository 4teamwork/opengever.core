from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String


class AddDefaultSettingsTable(SchemaMigration):

    profileid = 'opengever.activity'
    upgradeid = 4300

    def migrate(self):
        self.add_default_settings_table()

    def add_default_settings_table(self):
        self.op.create_table(
            'default_settings',
            Column("id", Integer, primary_key=True),
            Column("kind", String(50), nullable=False, unique=True),
            Column("mail_notification", Boolean, nullable=False, default=False)
        )
