from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddOrgRoleParticipations(SchemaMigration):
    """Add OrgRole participations.
    """

    def migrate(self):
        self.make_contact_id_nullable()

        self.add_participation_type()
        self.insert_contact_participation_type()
        self.make_participation_type_non_nullable()

        self.add_org_role_participation()

    def make_contact_id_nullable(self):
        self.op.alter_column('participations', 'contact_id',
                             nullable=True,
                             existing_type=Integer)

    def add_participation_type(self):
        self.op.add_column(
            'participations',
            Column('participation_type', String(30), nullable=True))

    def insert_contact_participation_type(self):
        participation_table = table(
            'participations', column('participation_type'))

        self.execute(participation_table.update().values(
            participation_type='contact_participation'))

    def make_participation_type_non_nullable(self):
        self.op.alter_column('participations', 'participation_type',
                             existing_type=String, nullable=False)

    def add_org_role_participation(self):
        self.op.add_column(
            'participations',
            Column('org_role_id', Integer, ForeignKey('org_roles.id')))
