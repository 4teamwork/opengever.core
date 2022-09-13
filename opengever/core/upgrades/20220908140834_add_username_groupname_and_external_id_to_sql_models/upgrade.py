from opengever.base.model import GROUP_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


users_table = table(
    'users',
    column('absent'),
    column('absent_from'),
    column('absent_to'),
    column('active'),
    column('address1'),
    column('address2'),
    column('city'),
    column('country'),
    column('department'),
    column('department_abbr'),
    column('description'),
    column('directorate'),
    column('directorate_abbr'),
    column('email'),
    column('email2'),
    column('external_id'),
    column('firstname'),
    column('lastname'),
    column('last_login'),
    column('phone_fax'),
    column('phone_mobile'),
    column('phone_office'),
    column('salutation'),
    column('title'),
    column('url'),
    column('userid'),
    column('username'),
    column('zip_code'),
)

groups_table = table(
    'groups',
    column('active'),
    column('external_id'),
    column('groupid'),
    column('groupname'),
    column('is_local'),
    column('title'),
)


class AddUsernameGroupnameAndExternalIdToSqlModels(SchemaMigration):
    """Add username groupname and external_id to sql models.
    """

    def migrate(self):
        self.op.add_column(
            'users', Column('username', String(USER_ID_LENGTH), nullable=True)
        )
        self.op.add_column(
            'users', Column('external_id', String(USER_ID_LENGTH), nullable=True, unique=True)
        )
        self.op.add_column(
            'groups', Column('groupname', String(GROUP_ID_LENGTH), nullable=True)
        )
        self.op.add_column(
            'groups', Column('external_id', String(GROUP_ID_LENGTH), nullable=True, unique=True)
        )

        self.execute(users_table.update().values(
            external_id=users_table.c.userid, username=users_table.c.userid))
        self.execute(groups_table.update().values(
            external_id=groups_table.c.groupid, groupname=groups_table.c.groupid))

        self.op.alter_column('users', 'username', existing_type=String, nullable=False)
        self.op.alter_column('users', 'external_id', existing_type=String, nullable=False)
        self.op.alter_column('groups', 'groupname', existing_type=String, nullable=False)
        self.op.alter_column('groups', 'external_id', existing_type=String, nullable=False)
