from opengever.core.upgrade import SQLUpgradeStep
from opengever.ogds.base.utils import get_current_admin_unit
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


proposals_table = table(
    "proposals",
    column("submitted_int_id"),
    column("submitted_admin_unit_id"),
    column("submitted_title"),
)


class FixSubmittedProposalTitleSync(SQLUpgradeStep):
    """Fix submitted proposal title sync.
    """

    def migrate(self):
        self.admin_unit_id = get_current_admin_unit().id()
        self.intids = getUtility(IIntIds)

        self.resync_submitted_proposal_title()

    def resync_submitted_proposal_title(self):
        for submitted_proposal in self.objects(
                {'portal_type': 'opengever.meeting.submittedproposal'},
                'Fix submitted proposal title sync.'):

            intid = self.intids.getId(submitted_proposal)
            title = submitted_proposal.title

            self.execute(proposals_table.update()
                .values(submitted_title=title)
                .where(proposals_table.c.submitted_admin_unit_id == self.admin_unit_id)
                .where(proposals_table.c.submitted_int_id == intid))
