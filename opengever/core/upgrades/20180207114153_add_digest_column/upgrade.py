from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddDigestColumn(SchemaMigration):
    """Add is_digest and sent_in_digest column.
    """

    def migrate(self):
        self.op.add_column(
            'notifications',
            Column('is_digest', Boolean, default=False))
        self.op.add_column(
            'notifications',
            Column('sent_in_digest', Boolean, default=False))
        self.op.add_column('notification_defaults',
                           Column('digest_notification_roles', Text))
        self.op.add_column('notification_settings',
                           Column('digest_notification_roles', Text))

        # Insert default-values (mark all existing notifications as sent)
        notifications_table = table(
            'notifications', column("id"), column("sent_in_digest"))
        self.connection.execute(
            notifications_table.update().values(sent_in_digest=True))

        # Make column non-nullable
        self.op.alter_column('notifications', 'sent_in_digest',
                             existing_type=Boolean, nullable=False)
