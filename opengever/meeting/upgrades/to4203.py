from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import String


class AddMembershipRole(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4203

    def migrate(self):
        self.add_role_to_membership()

    def add_role_to_membership(self):
        self.op.add_column('memberships', Column('role', String(256)))
