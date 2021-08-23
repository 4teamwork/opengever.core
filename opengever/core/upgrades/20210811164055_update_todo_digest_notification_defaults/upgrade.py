from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("digest_notification_roles")
)

KINDS_TO_MIGRATE = ('todo-assigned', 'todo-modified')


class UpdateTodoDigestNotificationDefaults(SchemaMigration):
    """Update todo digest notification defaults.
    """
    def migrate(self):
        self.update_notification_defaults()

    def update_notification_defaults(self):
        for kind in KINDS_TO_MIGRATE:
            self.execute(
                defaults_table.update()
                .values(digest_notification_roles=json.dumps([]))
                .where(defaults_table.columns.kind == kind)
            )
