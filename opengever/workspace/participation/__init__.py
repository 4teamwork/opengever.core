from zope.i18n import translate
from opengever.workspace import _


class ParticipationRole(object):
    def __init__(self, id_, title, managed):
        self.id = id_
        self.title = title
        self.managed = managed

    def translated_title(self, request):
        return translate(self.title, context=request)

    def serialize(self, request):
        return {
            'id': self.id,
            'title': self.translated_title(request),
            'managed': self.managed
        }

WORKSPCAE_GUEST = ParticipationRole(
    'WorkspaceGuest', _('WorkspaceGuest', default="Guest"), True)
WORKSPCAE_MEMBER = ParticipationRole(
    'WorkspaceMember', _('WorkspaceMember', default="Member"), True)
WORKSPCAE_ADMIN = ParticipationRole(
    'WorkspaceAdmin', _('WorkspaceAdmin', default="Admin"), True)
WORKSPCAE_OWNER = ParticipationRole(
    'WorkspaceOwner', _('WorkspaceOwner', default="Owner"), False)

PARTICIPATION_ROLES = {
    WORKSPCAE_GUEST.id: WORKSPCAE_GUEST,
    WORKSPCAE_OWNER.id: WORKSPCAE_OWNER,
    WORKSPCAE_ADMIN.id: WORKSPCAE_ADMIN,
    WORKSPCAE_MEMBER.id: WORKSPCAE_MEMBER
}
