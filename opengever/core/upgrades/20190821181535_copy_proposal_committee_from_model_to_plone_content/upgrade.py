from opengever.core.upgrade import SQLUpgradeStep
from opengever.base.oguid import Oguid
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import join
from sqlalchemy.sql.expression import table
from sqlalchemy.sql import select


proposals_table = table(
    "proposals",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
    column("submitted_admin_unit_id"),
    column("submitted_int_id"),
    column("committee_id"),
)

committees_table = table(
    "committees",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
)


class CopyProposalCommitteeFromModelToPloneContent(SQLUpgradeStep):
    """Copy proposal committee from model to plone content.
    """

    def migrate(self):
        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal']},
                'Copy committee_oguid field from model to plone content.'):
            oguid = Oguid.for_object(proposal)

            join_expr = join(
                proposals_table, committees_table,
                proposals_table.c.committee_id == committees_table.c.id)
            row = self.execute(
                select([committees_table])
                .where(proposals_table.c.admin_unit_id == oguid.admin_unit_id)
                .where(proposals_table.c.int_id == oguid.int_id)
                .select_from(join_expr)).fetchone()

            proposal.committee_oguid = Oguid(row.admin_unit_id, row.int_id).id

        for submitted_proposal in self.objects(
                {'portal_type': ['opengever.meeting.submittedproposal']},
                'Copy committee_oguid field from model to plone content.'):
            oguid = Oguid.for_object(submitted_proposal)

            join_expr = join(
                proposals_table, committees_table,
                proposals_table.c.committee_id == committees_table.c.id)
            row = self.execute(
                select([committees_table])
                .where(proposals_table.c.submitted_admin_unit_id == oguid.admin_unit_id)
                .where(proposals_table.c.submitted_int_id == oguid.int_id)
                .select_from(join_expr)).fetchone()

            submitted_proposal.committee_oguid = Oguid(row.admin_unit_id, row.int_id).id
