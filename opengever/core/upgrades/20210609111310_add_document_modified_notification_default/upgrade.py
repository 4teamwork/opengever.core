from opengever.activity.roles import WATCHER_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


SETTING = {
    'kind': 'document-modified',
    'badge_notification_roles': [WATCHER_ROLE],
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


class AddDocumentModifiedNotificationDefault(SchemaMigration):
    """Add document modified notification default.
    """

    def migrate(self):
        self.insert_notification_defaults()

    def insert_notification_defaults(self):
        seq = Sequence('notification_defaults_id_seq')
        self.execute(defaults_table
                     .insert()
                     .values(id=self.execute(seq),
                             kind=SETTING['kind'],
                             badge_notification_roles=json.dumps(SETTING['badge_notification_roles']),
                             mail_notification_roles=json.dumps(SETTING['mail_notification_roles']),
                             digest_notification_roles=json.dumps(SETTING['digest_notification_roles'])))
