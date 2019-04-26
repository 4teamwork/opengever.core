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


class ParticipationType(object):
    def __init__(self, id_, title, path_identifier):
        self.id = id_
        self.title = title
        self.path_identifier = path_identifier

    def translated_title(self, request):
        return translate(self.title, context=request)

    def serialize(self, request):
        return {
            'id': self.id,
            'title': self.translated_title(request)
        }

TYPE_USER = ParticipationType('user', _('user', default="User"), 'users')
TYPE_INVITATION = ParticipationType('invitation',
                                    _('invitation', default="Invitation"),
                                    'invitations')

PARTICIPATION_TYPES = {
    TYPE_USER.id: TYPE_USER,
    TYPE_INVITATION.id: TYPE_INVITATION,
}

PARTICIPATION_TYPES_BY_PATH_IDENTIFIER = {
    value.path_identifier: value for value in PARTICIPATION_TYPES.values()}
