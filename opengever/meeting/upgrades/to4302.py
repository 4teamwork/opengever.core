from opengever.core.upgrade import SchemaMigration
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import CreateSequence
from sqlalchemy.schema import Sequence
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


class AddMembershipIdColumn(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4302

    def migrate(self):
        self.rename_table()
        self.create_new_table()
        self.migrate_data()

    def rename_table(self):
        self.op.rename_table('memberships', 'tmp_memberships')

    def create_new_table(self):
        self.membership_table = self.op.create_table(
            'memberships',
            Column("id", Integer, Sequence("membership_id_seq"),
                   primary_key=True),
            Column("date_from", Date, nullable=False),
            Column("date_to", Date, nullable=False),
            Column("committee_id", Integer, ForeignKey('committees.id')),
            Column("member_id", Integer, ForeignKey('members.id')),
            Column("role", String(256))
        )

        self.op.execute(CreateSequence(Sequence("membership_id_seq")))

        self.op.create_unique_constraint(
            'ix_membership_unique',
            'memberships',
            ['committee_id', 'member_id', 'date_from'])

    def migrate_data(self):
        tmp_membership_table = table(
            "tmp_memberships",
            column("date_from"),
            column("date_to"),
            column("committee_id"),
            column("member_id"),
            column("role"),
        )

        memberships = self.connection.execute(tmp_membership_table.select()).fetchall()
        for membership in memberships:
            self.execute(
                self.membership_table.insert(values={
                    'date_from':membership.date_from,
                    'date_to':membership.date_to,
                    'committee_id':membership.committee_id,
                    'member_id':membership.member_id,
                    'role':membership.role,
                })
            )
