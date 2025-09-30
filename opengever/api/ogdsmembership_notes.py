from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.interface import alsoProvides


class MembershipNotes(Service):
    """POST @ogds-groups/{groupid}/@membership-notes
    Payload:
    {
      "members": [
        {"userid": "pmuster", "note": "President"},
        {"userid": "smeier",  "note": "Secretary"},
        {"userid": "lmeier",  "note": ""}  # empty => clear
      ]
    }
    """

    def reply(self):
        if not self._is_admin():
            raise Unauthorized("Admin only")

        data = self.request.get_json() or {}
        members = data.get("members")
        if not isinstance(members, list):
            raise BadRequest("members must be a list")

        group = self.context
        by_userid = {m.userid: m for m in group.memberships}

        updated, cleared = [], []
        for item in members:
            userid = item.get("userid")
            if not userid or userid not in by_userid:
                raise BadRequest(f"user {userid!r} not a member of this group")
            m = by_userid[userid]
            note = (item.get("note") or "").strip()
            m.note = note or None
            (cleared if not note else updated).append(userid)

        create_session().flush()
        return {"updated": updated, "cleared": cleared}

    def _is_admin(self):
        mtool = getToolByName(self.context, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        return user and user.has_role(['Manager', 'Administrator'])
