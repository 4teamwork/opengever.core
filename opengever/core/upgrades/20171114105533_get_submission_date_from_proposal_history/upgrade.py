from opengever.core.upgrade import SQLUpgradeStep
from opengever.ogds.base.utils import get_current_admin_unit
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from opengever.meeting.interfaces import IHistory


proposals_table = table(
    "proposals",
    column("int_id"),
    column("admin_unit_id"),
    column("submitted_int_id"),
    column("submitted_admin_unit_id"),
    column("date_of_submission"),
)


class GetSubmissionDateFromProposalHistory(SQLUpgradeStep):
    """Get submission date from proposal history."""

    def migrate(self):
        self.admin_unit_id = get_current_admin_unit().id()
        self.intids = getUtility(IIntIds)

        self.migrate_proposals()
        self.migrate_submitted_proposals()

    def migrate_proposals(self):
        for proposal in self.objects(
                {'portal_type': 'opengever.meeting.proposal'},
                'Update proposal submission date.'):
            self.migrate_proposal(proposal)

    def migrate_proposal(self, proposal):
        """A proposal may not have been submitted, or have been rejected
        after the submission. In that case do nothing.
        """
        intid = self.intids.getId(proposal)
        date_of_submission = self.get_date_of_submission_from_history(proposal)

        if not date_of_submission:
            return

        proposal.date_of_submission = date_of_submission
        self.execute(
            proposals_table.update()
            .values(date_of_submission=date_of_submission)
            .where(proposals_table.c.admin_unit_id == self.admin_unit_id)
            .where(proposals_table.c.int_id == intid)
        )

    def migrate_submitted_proposals(self):
        for submitted_proposal in self.objects(
                {'portal_type': 'opengever.meeting.submittedproposal'},
                'Update submitted proposal submission date.'):
            self.migrate_submitted_proposal(submitted_proposal)

    def migrate_submitted_proposal(self, submitted_proposal):
        """A submitted proposal must always be submitted. The submitted
        proposal would have been removed if it was rejected. So if there is no
        history record for some reason (may have been migrated from a very
        old version?) fall back to plone object creation timestamp.
        """
        intid = self.intids.getId(submitted_proposal)
        date_of_submission = self.get_date_of_submission_from_history(submitted_proposal)

        if not date_of_submission:
            date_of_submission = submitted_proposal.created().asdatetime().date()

        submitted_proposal.date_of_submission = date_of_submission
        self.execute(
            proposals_table.update()
            .values(date_of_submission=date_of_submission)
            .where(proposals_table.c.submitted_admin_unit_id == self.admin_unit_id)
            .where(proposals_table.c.submitted_int_id == intid)
        )

    def get_date_of_submission_from_history(self, proposal):
        """Find date of submission for (submitted-)proposal in history.

        Go through history from oldest to newest and return date of submission.
        If it was rejected after being submitted, return None.
        """
        date_of_submission = None

        for record in reversed(list(IHistory(proposal))):
            if record.history_type == 'submitted':
                date_of_submission = record.created.date()
            elif record.history_type == 'rejected':
                date_of_submission = None

        return date_of_submission
