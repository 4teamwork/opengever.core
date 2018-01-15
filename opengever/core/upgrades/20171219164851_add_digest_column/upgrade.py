from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Text


class AddDigestColumn(SchemaMigration):
    """Add digest column.
    """

    def migrate(self):
        self.op.add_column(
            'notifications',
            Column('is_digest', Boolean, default=False))

        self.op.add_column('notification_defaults',
                           Column('digest_notification_roles', Text))
        self.op.add_column('notification_settings',
                           Column('digest_notification_roles', Text))
