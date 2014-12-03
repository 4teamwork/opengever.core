from opengever.core.upgrade import DeactivatedFKConstraint
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import String


class IncreaseColumnLength(SchemaMigration):
    """The userid colum in the users table was already increased
    by an earlier change see
    https://github.com/4teamwork/opengever.ogds.models/commit/daaa420a
    """

    profileid = 'opengever.ogds.base'
    upgradeid = 4006

    def migrate(self):
        self.increase_userid_length()
        self.increase_groupid_length()

    def increase_length(self, tablename, column, existing_type, new_type,
                        fk_table_name, source_cols, referent_cols):

        fk_name = self.get_foreign_key_name(tablename, column)

        with DeactivatedFKConstraint(self.op, fk_name,
                                     tablename, fk_table_name,
                                     source_cols, referent_cols):

            self.op.alter_column(tablename,
                                 column,
                                 type_=new_type,
                                 existing_nullable=False,
                                 existing_type=existing_type)

    def increase_userid_length(self):
        self.increase_length('groups_users', 'userid',
                             String(30), String(255),
                             fk_table_name='users',
                             source_cols=['userid'],
                             referent_cols=['userid'])

    def increase_groupid_length(self):
        self.increase_length('groups_users', 'groupid',
                             String(50), String(255),
                             fk_table_name='groups',
                             source_cols=['groupid'],
                             referent_cols=['groupid'])

        self.increase_length('org_units', 'users_group_id',
                             String(30), String(255),
                             fk_table_name='groups',
                             source_cols=['users_group_id'],
                             referent_cols=['groupid'])

        self.increase_length('org_units', 'inbox_group_id',
                             String(30), String(255),
                             fk_table_name='groups',
                             source_cols=['inbox_group_id'],
                             referent_cols=['groupid'])
