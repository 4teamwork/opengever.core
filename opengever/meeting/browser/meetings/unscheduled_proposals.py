from opengever.base.response import JSONResponse
from opengever.meeting import _
from opengever.meeting.model import Proposal
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class UnscheduledProposalsView(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    def __init__(self, context, request):
        super(UnscheduledProposalsView, self).__init__(context, request)
        self.meeting = self.context.model
        self.proposal_id = None

    def publishTraverse(self, request, name):
        if name == 'schedule':
            return self.schedule_proposal

        # we only support exactly one id
        if self.proposal_id:
            raise NotFound
        self.proposal_id = int(name)
        return self

    def schedule_url(self, proposal):
        return '{}/unscheduled_proposals/{}/schedule'.format(
            self.context.absolute_url(), proposal.proposal_id)

    def check_editable(self):
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")

    def schedule_proposal(self):
        """Schedule the current proposal on the current meeting.
        """
        self.check_editable()

        proposal = Proposal.get(self.proposal_id)
        if not proposal:
            raise NotFound

        self.meeting.schedule_proposal(proposal)
        return JSONResponse(self.request).info(
            _('Scheduled Successfully')).proceed().dump()

    def __call__(self):
        """Schedule the current proposal on the current meeting.
        """
        proposals = map(lambda proposal: {
            'title': proposal.resolve_submitted_proposal().title,
            'submitted_proposal_url': proposal.get_submitted_url(),
            'schedule_url': self.schedule_url(proposal)},
                        self.context.get_unscheduled_proposals())

        return JSONResponse(self.request).data(items=proposals).dump()
