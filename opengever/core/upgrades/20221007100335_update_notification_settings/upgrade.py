from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
)

settings_table = table(
    "notification_settings",
    column("id"),
    column("kind"),
)


class UpdateNotificationSettings(SchemaMigration):
    """Update notification settings.
    """

    def migrate(self):
        self.execute(
            defaults_table.update()
            .values(kind='task-modified')
            .where(defaults_table.columns.kind == 'task-transition-modify-deadline')
        )
        self.execute(
            settings_table.update()
            .values(kind='task-modified')
            .where(settings_table.columns.kind == 'task-transition-modify-deadline')
        )
