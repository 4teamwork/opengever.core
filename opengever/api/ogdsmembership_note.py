from opengever.base.model import create_session
from opengever.ogds.models.group_membership import GroupMembership
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from sqlalchemy import and_
from zExceptions import BadRequest


class MembershipNotes(Service):

    def reply(self):
        data = json_body(self.request) or {}

        groupid = data.get('groupid')
        userid = data.get('userid')
        note = data.get('note', None)

        if not groupid or not userid:
            raise BadRequest("Groupid and Userid are required.")

        if isinstance(note, basestring):
            note = note.strip()
            normalized = note or None
        elif note is None:
            normalized = None
        else:
            raise BadRequest("Note must be a string or null.")

        session = create_session()
        membership = (session.query(GroupMembership)
                      .filter(and_(GroupMembership.groupid == groupid,
                                   GroupMembership.userid == userid))
                      .one())

        membership.note = normalized
        session.flush()

        self.request.response.setStatus(200)
        return {
            "groupid": groupid,
            "userid": userid,
            "note": membership.note
        }
