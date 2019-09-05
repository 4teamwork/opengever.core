from opengever.base import advancedjson
from opengever.base.request import tracebackify
from opengever.base.security import as_internal_workflow_transition
from opengever.base.security import elevated_privileges
from opengever.base.utils import ok_response
from opengever.meeting.activity.activities import ProposalRemovedFromScheduleActivity
from opengever.meeting.activity.activities import ProposalScheduledActivity
from opengever.meeting.interfaces import IHistory
from plone import api
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
            IHistory(self.context).append_record(
                u'scheduled', meeting_id=meeting_id)
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
            IHistory(self.context).append_record(
                u'remove_scheduled', meeting_id=meeting_id)
            ProposalRemovedFromScheduleActivity(
                self.context, self.request, meeting_id).record()

        return ok_response(self.request)
