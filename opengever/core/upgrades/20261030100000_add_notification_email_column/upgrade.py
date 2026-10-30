from opengever.base.model import EMAIL_LENGTH
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddNotificationEmailColumn(SchemaMigration):
    """Add the local, private notification email setting."""

    def migrate(self):
        self.op.add_column(
            'user_settings',
            Column('notification_email', String(EMAIL_LENGTH), nullable=True))
