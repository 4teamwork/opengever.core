from opengever.base import advancedjson
from opengever.base.request import tracebackify
from opengever.base.response import IResponseContainer
from opengever.base.security import as_internal_workflow_transition
from opengever.base.security import elevated_privileges
from opengever.base.transport import PrivilegedReceiveObject
from opengever.base.utils import ok_response
from opengever.locking.lock import MEETING_EXCERPT_LOCK
from opengever.meeting.activity.activities import ProposalDecideActivity
from opengever.meeting.activity.activities import ProposalRejectedActivity
from opengever.meeting.activity.activities import ProposalRemovedFromScheduleActivity
from opengever.meeting.activity.activities import ProposalScheduledActivity
from opengever.meeting.proposalhistory import ProposalResponse
from plone import api
from plone.locking.interfaces import ILockable
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from zope.interface import alsoProvides


@tracebackify
class ReceiveProposalScheduled(BrowserView):
    """Receive a remote transition execution to schedule the proposal.

    This view is only available for internal requests.
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)  # internal request

        data = advancedjson.loads(self.request.get('data'))
        meeting_id = data['meeting_id']

        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-schedule')
            response = ProposalResponse(u'scheduled', meeting_id=meeting_id)
            IResponseContainer(self.context).add(response)
            ProposalScheduledActivity(
                self.context, self.request, meeting_id).record()

        return ok_response(self.request)


@tracebackify
class ReceiveProposalUnscheduled(BrowserView):
    """Receive a remote transition execution to unschedule the proposal.

    This view is only available for internal requests.
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)  # internal request

        data = advancedjson.loads(self.request.get('data'))
        meeting_id = data['meeting_id']

        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-unschedule')
            response = ProposalResponse(u'remove_scheduled', meeting_id=meeting_id)
            IResponseContainer(self.context).add(response)
            ProposalRemovedFromScheduleActivity(
                self.context, self.request, meeting_id).record()

        return ok_response(self.request)


class ReceiveProposalDecided(PrivilegedReceiveObject):
    """Receive a remote transition execution to decide the proposal.

    Receive the excerpt document that is required to set a proposal to decided
    as it should contain some form of decision. Lock excerpt document after
    recieving it.

    This view is only available for internal requests.
    """
    @property
    def container(self):
        """Return the parent dossier as container for the excerpt."""

        return self.context.get_containing_dossier()

    def receive(self):
        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-decide')
            response = ProposalResponse(u'decided')
            IResponseContainer(self.context).add(response)
            ProposalDecideActivity(self.context, self.request).record()

        document = super(ReceiveProposalDecided, self).receive()
        ILockable(document).lock(MEETING_EXCERPT_LOCK)
        return document


@tracebackify
class ReceiveProposalRejected(BrowserView):
    """Receive a remote transition execution to reject the proposal.

    This view is only available for internal requests.
    """
    def __call__(self):
        data = advancedjson.loads(self.request.get('data'))
        text = data['text']

        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-reject')
            response = ProposalResponse(u'rejected', text=text)
            IResponseContainer(self.context).add(response)
            ProposalRejectedActivity(self.context, self.request).record()

            self.context.date_of_submission = None

        return ok_response(self.request)
