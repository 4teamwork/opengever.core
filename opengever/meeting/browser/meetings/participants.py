from functools import wraps
from opengever.base.response import JSONResponse
from opengever.meeting import _
from opengever.meeting.model.membership import Membership
from Products.Five.browser import BrowserView
from zope.interface import Interface
import json


MSG_SAVE_FAILURE = _(u'Failed to save.')
MSG_NOT_ALLOWED_TO_CHANGE_MEETING = _(
    u'You are not allowed to change the meeting details.')


class IParticipantsActions(Interface):

    def change_role():
        """Change the role of a participant.
        """

    def change_presence():
        """Change the presence of a participant.
        """


def require_meeting_edit_permission(func):
    """Decorator for protecting an endpoint to require an editable meeting.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.meeting.is_editable():
            return (JSONResponse(self.request)
                    .error(MSG_NOT_ALLOWED_TO_CHANGE_MEETING)
                    .remain()
                    .dump())
        return func(self, *args, **kwargs)
    return wrapper


class ParticipantsView(BrowserView):

    def __init__(self, context, request):
        super(ParticipantsView, self).__init__(context, request)
        self.meeting = self.context.model

    @require_meeting_edit_permission
    def change_role(self):
        """Change the role of a participant.
        """
        response = JSONResponse(self.request)
        role = self.request.form.get('role', None)
        member = self.get_member()
        if role is None or member is None:
            return response.error(MSG_SAVE_FAILURE).remain().dump()

        if self.meeting.presidency == member:
            self.meeting.presidency = None
        if self.meeting.secretary == member:
            self.meeting.secretary = None

        if role == 'presidency':
            self.meeting.presidency = member
        elif role == 'secretary':
            self.meeting.secretary = member
        return response.proceed().dump()

    @require_meeting_edit_permission
    def change_presence(self):
        """Change the presence of a participant.
        """
        response = JSONResponse(self.request)
        present = self.request.form.get('present', None)
        member = self.get_member()
        if not present or not member:
            return response.error(MSG_SAVE_FAILURE).remain().dump()

        present = json.loads(present)
        if present and member not in self.meeting.participants:
            self.meeting.participants.append(member)
        elif not present and member in self.meeting.participants:
            self.meeting.participants.remove(member)
        return response.proceed().dump()

    def get_member(self):
        member_id = self.request.form.get('member_id', None)
        if not member_id:
            return None

        membership = Membership.query.for_meeting(self.meeting).filter_by(
            member_id=member_id).first()
        if membership:
            return membership.member

        member_id = int(member_id)
        for member in self.meeting.participants:
            if member.member_id == member_id:
                return member
        return None
