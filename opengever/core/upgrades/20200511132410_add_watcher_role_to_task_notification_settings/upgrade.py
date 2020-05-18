from opengever.core.upgrade import SchemaMigration
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from opengever.activity.model import NotificationSetting
from opengever.activity.notification_settings import NotificationSettings
import json

DEFAULT_SETTINGS = [
    {
        'kind': 'task-added-or-reassigned',
        'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE, WATCHER_ROLE]
    },
    {
        'kind': 'task-transition-modify-deadline',
        'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE, WATCHER_ROLE]
    },
    {
        'kind': 'task-commented',
        'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE, WATCHER_ROLE]
    },
    {
        'kind': 'task-status-modified',
        'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE, WATCHER_ROLE]
    }
]

defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"))


class AddWatcherRoleToTaskNotificationSettings(SchemaMigration):
    """Add watcher role to task notification settings.
    """

    def migrate(self):
        self.update_notification_defaults()
        self.migrate_user_settings()

    def update_notification_defaults(self):
        for item in DEFAULT_SETTINGS:

            self.execute(
                defaults_table.update()
                .values(badge_notification_roles=json.dumps(item['badge_notification_roles']))
                .where(defaults_table.columns.kind == item.get('kind'))
            )

    def migrate_user_settings(self):
        kinds = [default_setting.get('kind') for default_setting in DEFAULT_SETTINGS]
        settings = NotificationSetting.query.filter(NotificationSetting.kind.in_(kinds))
        for setting in settings:
            notification_roles = [role for role in setting.badge_notification_roles]
            notification_roles.append(WATCHER_ROLE)
            setting.badge_notification_roles = notification_roles
