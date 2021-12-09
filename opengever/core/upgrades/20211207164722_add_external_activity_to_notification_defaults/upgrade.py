from opengever.activity.roles import ALWAYS
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


DEFAULT_SETTING = {
    'kind': 'external-activity',
    'badge_notification_roles': [ALWAYS],
    'mail_notification_roles': [],
    'digest_notification_roles': [],
}


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"),
    column("mail_notification_roles"),
    column("digest_notification_roles"))


class AddExternalActivityToNotificationDefaults(SchemaMigration):
    """Add notification defaults for external-activity.
    """
    def migrate(self):
        self.insert_notification_defaults()

    def insert_notification_defaults(self):
        seq = Sequence('notification_defaults_id_seq')
        badge = json.dumps(DEFAULT_SETTING['badge_notification_roles'])
        mail = json.dumps(DEFAULT_SETTING['mail_notification_roles'])
        digest = json.dumps(DEFAULT_SETTING['digest_notification_roles'])
        self.execute(
            defaults_table
            .insert()
            .values(id=self.execute(seq),
                    kind=DEFAULT_SETTING['kind'],
                    badge_notification_roles=badge,
                    mail_notification_roles=mail,
                    digest_notification_roles=digest))
