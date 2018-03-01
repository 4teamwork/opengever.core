from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json

# copied from opengever.activity.roles
TASK_RESPONSIBLE_ROLE = 'task_responsible'
TASK_ISSUER_ROLE = 'task_issuer'

# copied from opengever.activity
DEFAULT_SETTINGS = [
    {'kind': 'task-added',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-cancelled-open',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-delegate',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-in-progress-resolved',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-in-progress-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-modify-deadline',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-cancelled',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-in-progress',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-rejected',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-resolved',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-open-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-commented',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-reassign',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-rejected-open',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-resolved-in-progress',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'task-transition-resolved-tested-and-closed',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-added',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-accept',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-assign-to-dossier',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-close',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-reassign',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-reassign-refused',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
    {'kind': 'forwarding-transition-refuse',
     'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE]},
]


class FixNotficationdefaultsBadgeRoles(SchemaMigration):
    """Fix Notficationdefaults badge roles.

    The `insert_notification_defaults` profile hook, has been created wrong
    entries for the badge_notification_roles column. This Upgradestep fix them.
    """

    def migrate(self):
        defaults_table = table(
            "notification_defaults",
            column("id"),
            column("kind"),
            column("badge_notification_roles"),
        )

        defaults = {item.get('kind'): item.get('badge_notification_roles')
                    for item in DEFAULT_SETTINGS}

        settings = self.connection.execute(defaults_table.select()).fetchall()
        for setting in settings:
            if setting.badge_notification_roles is None:
                roles = defaults.get(setting.kind, [])
                self.execute(
                    defaults_table.update()
                    .values(badge_notification_roles=json.dumps(roles))
                    .where(defaults_table.columns.id == setting.id)
                )
