from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import table


groups_table = table(
    'groups',
    column('active'),
    column('external_id'),
    column('groupid'),
    column('groupname'),
    column('is_local'),
    column('title'),
)

groups_users_table = table(
    'groups_users',
    column('groupid'),
    column('userid'),
)


class RemoveInactiveGroupMemberships(SchemaMigration):
    """Remove inactive group memberships.
    """

    def migrate(self):
        if self.is_oracle:
            rows = self.execute(
                select([groups_table.c.groupid])
                .where(groups_table.c.active == False)  # noqa
                .where(groups_table.c.is_local == False)  # noqa
            ).fetchall()
        else:
            rows = self.execute(
                select([groups_table.c.groupid])
                .where(groups_table.c.active.is_(False))
                .where(groups_table.c.is_local.is_(False))
            ).fetchall()

        groupids = [row[0] for row in rows]

        self.execute(
            groups_users_table.delete()
            .where(groups_users_table.c.groupid.in_(groupids)))
