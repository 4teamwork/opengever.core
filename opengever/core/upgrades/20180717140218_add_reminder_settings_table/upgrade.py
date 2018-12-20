from opengever.base.model import USER_ID_LENGTH
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class AddReminderSettingsTable(SchemaMigration):
    """Add reminder settings table.
    """

    def migrate(self):
        self.op.create_table(
            'reminder_settings',
            Column('id', Integer, Sequence('reminder_setting_id_seq'), primary_key=True),
            Column('task_id', Integer, ForeignKey('tasks.id'), nullable=False),
            Column('actor_id', String(USER_ID_LENGTH), index=True, nullable=False),
            Column('option_type', String(255), nullable=False),
            Column('remind_day', Date, nullable=False),
            Column('created', DateTime(timezone=True)),
        )

        self.ensure_sequence_exists('reminder_setting_id_seq')
