from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import json


DEFAULT_SETTINGS = [

    {'kind': 'disposition-added',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
     'mail_notification_roles': [DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-appraise',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-archive',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-close',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-appraised-to-closed',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-dispose',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},
    {'kind': 'disposition-transition-refuse',
     'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE]},

]


defaults_table = table(
    "notification_defaults",
    column("id"),
    column("kind"),
    column("badge_notification_roles"),
    column("mail_notification_roles"))


class AddDispositionActivitySettings(SchemaMigration):
    """Add notification settings for disposition.
    """

    def migrate(self):
        self.insert_notification_defaults()

    def insert_notification_defaults(self):
        seq = Sequence('notification_defaults_id_seq')
        for item in DEFAULT_SETTINGS:
            setting = self.execute(defaults_table
                                   .select()
                                   .where(defaults_table.columns.kind == item.get('kind')))

            if setting.rowcount:
                # We don't want to reset already inserted settings
                continue

            self.execute(defaults_table
                         .insert()
                         .values(id=self.execute(seq),
                                 kind=item['kind'],
                                 badge_notification_roles=json.dumps(item['badge_notification_roles']),
                                 mail_notification_roles=json.dumps(item.get('mail_notification_roles', []))))
