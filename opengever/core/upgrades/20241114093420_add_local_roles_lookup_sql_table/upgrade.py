from opengever.base.types import JSONList
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String


UNIT_ID_LENGTH = 30
USER_ID_LENGTH = 255
UID_LENGTH = 36


class AddLocalRolesLookupSqlTable(SchemaMigration):
    """Add local roles lookup sql table.
    """
    def migrate(self):
        self.op.create_table(
            'local_roles',
            Column('admin_unit_id', String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'),
                   nullable=False, primary_key=True),
            Column('principal_id', String(USER_ID_LENGTH), nullable=False, primary_key=True),
            Column('object_uid', String(UID_LENGTH), nullable=False, primary_key=True),
            Column('roles', JSONList(), nullable=True),
        )
