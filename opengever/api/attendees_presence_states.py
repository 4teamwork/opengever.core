from opengever.api import _
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.workspace.interfaces import IWorkspaceMeetingAttendeesPresenceStateStorage
from opengever.workspace.workspace_meeting import ALLOWED_ATTENDEES_PRESENCE_STATES
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class AttendeesPreseneceStatesPatch(Service):
    """Edit presence states of workspace meeting attendees.
    """

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)
        data = json_body(self.request)
        for userid, state in data.items():
            if userid not in self.context.attendees:
                raise NotReportedBadRequest(
                    _(u'userid_not_in_attendees',
                      default=u'User with userid ${userid} is not a participant in this meeting.',
                      mapping={'userid': userid}))
            if state not in ALLOWED_ATTENDEES_PRESENCE_STATES.keys():
                raise NotReportedBadRequest(
                    _(u'invalid_presence_state',
                      default=u'State ${state} does not exist.',
                      mapping={'state': state}))
            IWorkspaceMeetingAttendeesPresenceStateStorage(self.context).add_or_update(userid, state)
        return self.reply_no_content()
