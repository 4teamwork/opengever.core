from opengever.core.upgrade import SchemaMigration
from opengever.ogds.base.utils import get_current_org_unit
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddGroupIdColumn(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4608

    def migrate(self):
        self.add_group_id_column()
        self.insert_org_units_group_id()
        self.make_group_id_non_nullable()

    def add_group_id_column(self):
        self.op.add_column(
            'committees',
            Column('group_id', String(255), nullable=True))

    def insert_org_units_group_id(self):
        """Insert the current org-unit's group_id for all committees.

        Bye default we use the users group. This choice is somewhat arbitrary,
        but id does not really matter since meeting is not in production when
        this upgrade is executed.

        """
        proposal_table = table("committees",
                               column("id"),
                               column("group_id"))
        group_id = get_current_org_unit().users_group.groupid

        self.execute(
            proposal_table.update().values(group_id=group_id))

    def make_group_id_non_nullable(self):
        self.op.alter_column('committees', 'group_id',
                             existing_type=String(255), nullable=False)
