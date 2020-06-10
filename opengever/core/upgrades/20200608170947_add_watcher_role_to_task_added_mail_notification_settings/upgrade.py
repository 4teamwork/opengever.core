from opengever.core.upgrade import SchemaMigration
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from opengever.activity.model import NotificationSetting
import json

DEFAULT_SETTINGS = [
    {
        'kind': 'task-added-or-reassigned',
        'mail_notification_roles': [TASK_RESPONSIBLE_ROLE, WATCHER_ROLE]
    },
]

defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("mail_notification_roles"))


class AddWatcherRoleToTaskAddedMailNotificationSettings(SchemaMigration):
    """Add watcher role to task added mail notification settings.
    """

    def migrate(self):
        self.update_notification_defaults()
        self.migrate_user_settings()

    def update_notification_defaults(self):
        for item in DEFAULT_SETTINGS:

            self.execute(
                defaults_table.update()
                .values(mail_notification_roles=json.dumps(item['mail_notification_roles']))
                .where(defaults_table.columns.kind == item.get('kind'))
            )

    def migrate_user_settings(self):
        kinds = [default_setting.get('kind') for default_setting in DEFAULT_SETTINGS]
        settings = NotificationSetting.query.filter(NotificationSetting.kind.in_(kinds))
        for setting in settings:
            notification_roles = [role for role in setting.mail_notification_roles]
            if TASK_RESPONSIBLE_ROLE not in notification_roles:
                # as TASK_RESPONSIBLE user explicitely did not want mails when
                # a task is created, accordingly we use that same default for
                # created tasks as watcher
                continue
            if WATCHER_ROLE in notification_roles:
                # user has already modified his settings
                continue
            notification_roles.append(WATCHER_ROLE)
            setting.mail_notification_roles = notification_roles
