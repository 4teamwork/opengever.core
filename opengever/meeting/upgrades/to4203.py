from opengever.core.upgrade import AbortUpgrade
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

    def make_start_date_primary_mysql(self):
        self.op.execute(
            "ALTER TABLE `memberships` DROP PRIMARY KEY, "
            "ADD PRIMARY KEY (`committee_id`, `member_id`, `date_from`);")

    def make_start_date_primary_postgres(self):
        self.op.execute(
            "ALTER TABLE memberships DROP CONSTRAINT memberships_pkey, "
            "ADD PRIMARY KEY (committee_id, member_id, date_from);")

    def make_start_date_primary_oracle(self):
        self.op.execute(
            "ALTER TABLE MEMBERSHIPS DROP PRIMARY KEY;")
        self.op.execute(
            "ALTER TABLE MEMBERSHIPS ADD PRIMARY KEY "
            "(COMMITTEE_ID, MEMBER_ID, DATE_FROM);")

    def make_start_date_primary(self):
        if self.is_postgres:
            self.make_start_date_primary_postgres()
        elif self.is_oracle:
            self.make_start_date_primary_oracle()
        elif self.is_mysql:
            self.make_start_date_primary_mysql()
        else:
            raise AbortUpgrade(
                "unsupported DB dialect {}".format(self.dialect_name))
