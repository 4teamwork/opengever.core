from opengever.core.upgrade import SQLUpgradeStep
from opengever.base.oguid import Oguid
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table


proposals_table = table(
    "proposals",
    column("id"),
    column("admin_unit_id"),
    column("int_id"),
    column("submitted_admin_unit_id"),
    column("submitted_int_id"),
    column("language"),
)


class CopyProposalLanguageFromModelToPloneContent(SQLUpgradeStep):
    """Copy proposal language from model to plone content.
    """

    def migrate(self):
        for proposal in self.objects(
                {'portal_type': ['opengever.meeting.proposal']},
                'Copy language field from model to plone content.'):
            oguid = Oguid.for_object(proposal)

            row = self.execute(
                    proposals_table.select()
                    .where(proposals_table.c.admin_unit_id == oguid.admin_unit_id)
                    .where(proposals_table.c.int_id == oguid.int_id)
                ).fetchone()
            proposal.language = row.language

        for submitted_proposal in self.objects(
                {'portal_type': ['opengever.meeting.submittedproposal']},
                'Copy language field from model to plone content.'):
            oguid = Oguid.for_object(submitted_proposal)

            row = self.execute(
                    proposals_table.select()
                    .where(proposals_table.c.submitted_admin_unit_id == oguid.admin_unit_id)
                    .where(proposals_table.c.submitted_int_id == oguid.int_id)
                ).fetchone()
            submitted_proposal.language = row.language
