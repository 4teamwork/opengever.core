from opengever.activity.model.subscription import TASK_ISSUER_ROLE
from opengever.activity.model.subscription import TASK_RESPONSIBLE_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json



BADGE_NOTIFICATION_DEFAULT = json.dumps([TASK_RESPONSIBLE_ROLE,
                                         TASK_ISSUER_ROLE])


class MakeBadgeIconAChannel(SchemaMigration):
    """Make badge icon a channel.
    """

    def migrate(self):
        self.op.add_column('notification_defaults',
                           Column('badge_notification_roles', Text))
        self.insert_badge_icon_settings()

        self.add_badge_column()

    def insert_badge_icon_settings(self):
        """Enable badge notification for all existing settings.
        """

        defaults_table = table(
            "notification_defaults",
            column("id"),
            column("badge_notification_roles"),
        )

        self.execute(defaults_table.update()
                     .values(badge_notification_roles=BADGE_NOTIFICATION_DEFAULT))

    def add_badge_column(self):
        self.op.add_column(
            'notifications',
            Column('badge', Boolean, default=False))

        notifications_table = table(
            "notifications",
            column("id"),
            column("badge"),
        )

        self.execute(notifications_table.update().values(badge=True))
