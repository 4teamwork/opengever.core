import json

from opengever.base import advancedjson
from opengever.base.response import IResponseContainer
from opengever.base.security import (as_internal_workflow_transition,
                                     elevated_privileges)
from opengever.base.transport import PrivilegedReceiveObject, Transporter
from opengever.base.utils import ok_response
from opengever.locking.lock import MEETING_EXCERPT_LOCK
from opengever.meeting.activity.activities import (
    ProposalDecideActivity, ProposalRejectedActivity,
    ProposalRemovedFromScheduleActivity, ProposalScheduledActivity)
from opengever.meeting.proposalhistory import ProposalResponse
from plone import api
from plone.locking.interfaces import ILockable
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from z3c.relationfield.event import addRelations
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds


class ReceiveProposalScheduled(BrowserView):
    """Receive a remote transition execution to schedule the proposal.

    This view is only available for internal requests.
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)  # internal request

        self.request.stdin.seek(0)
        data = json.loads(self.request.stdin.read())

        meeting_id = data['meeting_id']
        meeting_title = data.get('meeting_title', u'')

        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-schedule')
            response = ProposalResponse(
                u'scheduled',
                meeting_id=meeting_id,
                meeting_title=meeting_title
            )
            IResponseContainer(self.context).add(response)
            ProposalScheduledActivity(
                self.context, self.request, meeting_id).record()
            self.context.set_meeting_title(meeting_title)

            self.context.sync_with_model()
            self.context.reindexObject()

        return ok_response(self.request)


class ReceiveProposalUnscheduled(BrowserView):
    """Receive a remote transition execution to unschedule the proposal.

    This view is only available for internal requests.
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)  # internal request

        self.request.stdin.seek(0)
        data = json.loads(self.request.stdin.read())

        meeting_id = data['meeting_id']
        meeting_title = data.get('meeting_title', '')

        with elevated_privileges():
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=self.context, transition='proposal-transition-unschedule')
            response = ProposalResponse(
                u'remove_scheduled',
                meeting_id=meeting_id,
                meeting_title=meeting_title
            )
            IResponseContainer(self.context).add(response)
            ProposalRemovedFromScheduleActivity(
                self.context, self.request, meeting_id).record()

            self.context.sync_with_model()
            self.context.reindexObject()

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
        alsoProvides(self.request, IDisableCSRFProtection)  # internal request

        with elevated_privileges():
            # transition propsoal to decided state, if necessary
            if api.content.get_state(self.context) != 'proposal-state-decided':
                with as_internal_workflow_transition():
                    api.content.transition(
                        obj=self.context, transition='proposal-transition-decide')
                response = ProposalResponse(u'decided')
                IResponseContainer(self.context).add(response)
                ProposalDecideActivity(self.context, self.request).record()

            self.request.stdin.seek(0)
            data = json.loads(self.request.stdin.read())

            transporter = Transporter()
            document = transporter.receive_data(self.container, data)
            self.context.append_excerpt(document)

            ILockable(document).lock(MEETING_EXCERPT_LOCK)

            self.context.sync_with_model()
            self.context.reindexObject()

        return document


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

            self.context.sync_with_model()
            self.context.reindexObject()

        return ok_response(self.request)
