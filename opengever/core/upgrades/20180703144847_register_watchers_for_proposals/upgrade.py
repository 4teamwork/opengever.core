from opengever.core.upgrade import SchemaMigration
from opengever.meeting.activity.watchers import add_watcher_on_proposal_created
from opengever.meeting.activity.watchers import add_watchers_on_submitted_proposal_created


class RegisterWatchersForProposals(SchemaMigration):
    """Register watchers for proposals.
    """

    def migrate(self):
        for obj in self.objects({'portal_type': 'opengever.meeting.proposal'},
                                'Register watchers for proposals'):
            add_watcher_on_proposal_created(obj)

        for obj in self.objects(
            {'portal_type': 'opengever.meeting.submittedproposal'},
                'Register watchers for submitted proposals'):

            add_watchers_on_submitted_proposal_created(obj)
