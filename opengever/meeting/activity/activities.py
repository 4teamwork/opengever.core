from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity.base import BaseActivity
from opengever.meeting import _
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from plone import api


def actor_link():
    return Actor.lookup(api.user.get_current().id).get_link()


class ProposalCommentedActivitiy(BaseActivity):
    """Activity representation for commenting a proposal.
    """
    kind = 'proposal-commented'

    def __init__(self, context, request):
        super(ProposalCommentedActivitiy, self).__init__(context, request)

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('proposal_history_label_commented', u'Proposal commented by ${user}',
              mapping={'user': actor_link()}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        return {}


class ProposalTransitionActivity(BaseActivity):
    """Activity which represents a proposal transition change.
    """

    def __init__(self, context, request):
        super(ProposalTransitionActivity, self).__init__(context, request)

    @property
    def description(self):
        return {}

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])


class ProposalSubmittedActivity(ProposalTransitionActivity):
    kind = 'proposal-transition-submit'

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('proposal_history_label_submitted', u'Submitted by ${user}',
              mapping={'user': actor_link()}))


class ProposalRejectedActivity(ProposalTransitionActivity):
    kind = 'proposal-transition-reject'

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('proposal_history_label_rejected', u'Rejected by ${user}',
              mapping={'user': actor_link()}))


class ProposalScheduledActivity(ProposalTransitionActivity):
    kind = 'proposal-transition-schedule'

    def __init__(self, context, request, meeting_id):
        super(ProposalTransitionActivity, self).__init__(context, request)
        self.meeting_id = meeting_id

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('proposal_history_label_scheduled',
              u'Scheduled for meeting ${meeting} by ${user}',
              mapping={'meeting': self.get_meeting_title(self.meeting_id),
                       'user': actor_link()}))

    def get_meeting_title(self, meeting_id):
        meeting = Meeting.query.get(meeting_id)
        return meeting.get_title() if meeting else u''


class ProposalDecideActivity(ProposalTransitionActivity):
    kind = 'proposal-transition-decide'

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _('proposal_history_label_decided', u'Proposal decided by ${user}',
              mapping={'user': actor_link()}))


class ProposalDocumentUpdatedActivity(BaseActivity):
    """Activity representation for updating a proposals document.
    """
    kind = 'proposal-attachment-updated'

    def __init__(self, context, request, document_title, submitted_version):
        super(ProposalDocumentUpdatedActivity, self).__init__(context, request)
        self.document_title = document_title
        self.submitted_version = submitted_version

    @property
    def summary(self):
        return self.translate_to_all_languages(
            _(u'proposal_activity_label_document_updated',
              u'Submitted document ${title} updated to version ${version}',
              mapping={'title': self.document_title or '',
                       'version': self.submitted_version}))

    @property
    def label(self):
        return self.translate_to_all_languages(ACTIVITY_TRANSLATIONS[self.kind])

    @property
    def description(self):
        return {}
