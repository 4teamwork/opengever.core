from opengever.core.upgrade import SQLUpgradeStep
from opengever.ogds.base.utils import get_current_admin_unit
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


proposals_table = table(
    "proposals",
    column("int_id"),
    column("admin_unit_id"),
    column("submitted_int_id"),
    column("submitted_admin_unit_id"),
    column("title"),
    column("submitted_title"),
)


class SyncSubmittedProposalTitleToSql(SQLUpgradeStep):
    """Sync (submitted)-proposal title to sql.
    """

    def migrate(self):
        admin_unit_id = get_current_admin_unit().id()
        intids = getUtility(IIntIds)

        for proposal in self.objects(
                {'portal_type': 'opengever.meeting.proposal'},
                'Sync proposal title to SQL index'):

            intid = intids.getId(proposal)
            self.execute(
                proposals_table.update()
                .values(title=proposal.title)
                .where(
                    proposals_table.c.admin_unit_id == admin_unit_id)
                .where(
                    proposals_table.c.int_id == intid)
            )

        for submitted_proposal in self.objects(
                {'portal_type': 'opengever.meeting.submittedproposal'},
                'Sync submitted proposal title to SQL index'):

            intid = intids.getId(submitted_proposal)
            self.execute(
                proposals_table.update()
                .values(submitted_title=submitted_proposal.title)
                .where(
                    proposals_table.c.submitted_admin_unit_id == admin_unit_id)
                .where(
                    proposals_table.c.submitted_int_id == intid)
            )
