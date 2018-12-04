from opengever.base.model import USER_ID_LENGTH
from opengever.core.upgrade import SchemaMigration
from opengever.ogds.models.user import User  # noqa
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.schema import Sequence


class AddNotificationSettingsTable(SchemaMigration):
    """Add NotificationSettings table.
    """

    def migrate(self):
        self.add_notification_settings_table()

    def add_notification_settings_table(self):
        self.op.create_table(
            'notification_settings',
            Column('id', Integer,
                   Sequence('notification_settings_id_seq'), primary_key=True),

            Column('kind', String(50), nullable=False),
            Column('userid', String(USER_ID_LENGTH), ForeignKey(User.userid)),
            Column('badge_notification_roles', Text),
            Column('mail_notification_roles', Text))

        self.ensure_sequence_exists('notification_settings_id_seq')
