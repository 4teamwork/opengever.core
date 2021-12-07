from opengever.activity.model import NotificationSetting
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


OLD_WATCHER_ROLE = u'regular_watcher'
NEW_ALWAYS_ROLE = u'always'

DEFAULT_SETTINGS = [
    {
        'kind': 'added-as-watcher',
        'badge_notification_roles': [NEW_ALWAYS_ROLE]
    },
]

defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"),
    column("mail_notification_roles"),
    column("digest_notification_roles"),
)


class MigrateNotificationRoleForAddedAsWatcherActivityToAlways(SchemaMigration):
    """Migrate notification role for added-as-watcher activity to always.
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

        def regular_watcher_to_always(role):
            if role == OLD_WATCHER_ROLE:
                return NEW_ALWAYS_ROLE
            return role

        kinds = [default_setting.get('kind') for default_setting in DEFAULT_SETTINGS]
        settings = NotificationSetting.query.filter(NotificationSetting.kind.in_(kinds))
        for setting in settings:
            for channel in ('badge_notification_roles',
                            'mail_notification_roles',
                            'digest_notification_roles'):
                old_roles = [role for role in getattr(setting, channel, [])]
                if old_roles:
                    new_roles = map(regular_watcher_to_always, old_roles)
                    setattr(setting, channel, new_roles)
