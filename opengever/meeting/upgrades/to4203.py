from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddMembershipRole(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4203

    def migrate(self):
        self.add_role_to_membership()
        self.make_start_date_primary()

    def add_role_to_membership(self):
        self.op.add_column('memberships', Column('role', String(256)))

    def make_start_date_primary(self):
        """this works only under the assumption that we run the migration
        with mysql.

        Luckily this is true since it is not in use in production. And a first
        activation in production will be done by differently, i.e. by creating
        all tables with metadata.create_all().

        """
        self.op.execute(
            "ALTER TABLE `memberships` DROP PRIMARY KEY, "
            "ADD PRIMARY KEY (`committee_id`, `member_id`, `date_from`);")
