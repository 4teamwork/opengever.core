from opengever.core.upgrade import SchemaMigration
from opengever.meeting.activity.watchers import add_watcher_on_proposal_created
from opengever.meeting.activity.watchers import add_watchers_on_submitted_proposal_created
from opengever.meeting.proposal import ISubmittedProposal


class RegisterWatchersForProposals(SchemaMigration):
    """Register watchers for proposals.
    """

    def migrate(self):
        for obj in self.objects(
            {'portal_type': ['opengever.meeting.proposal', 'opengever.meeting.submittedproposal']},
                'Register watchers for proposals'):

            if ISubmittedProposal.providedBy(obj):
                add_watchers_on_submitted_proposal_created(obj)
            else:
                add_watcher_on_proposal_created(obj)
