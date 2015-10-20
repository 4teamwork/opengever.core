from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


USER_ID_LENGTH = 255


class RenameUserIdColumn(SchemaMigration):
    profileid = 'opengever.activity'
    upgradeid = 4506

    def migrate(self):
        self.op.alter_column('watchers', 'user_id',
                             new_column_name='actorid',
                             existing_nullable=False,
                             existing_type=String(USER_ID_LENGTH))
