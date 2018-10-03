from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"))


class ChangeTaskReminderNotificationSettingRole(SchemaMigration):
    """Change task reminder notification setting role.
    """

    def migrate(self):
        self.execute(
            defaults_table.update()
            .values(badge_notification_roles=json.dumps([TASK_REMINDER_WATCHER_ROLE]))
            .where(defaults_table.columns.kind == 'task-reminder')
            )
