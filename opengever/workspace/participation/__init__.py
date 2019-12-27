from itsdangerous import URLSafeTimedSerializer
from opengever.ogds.base.actor import PloneUserActor
from opengever.workspace import _
from opengever.workspace.config import workspace_config
from plone import api
from zope.i18n import translate


class ParticipationRole(object):
    def __init__(self, id_, title, managed):
        self.id = id_
        self.title = title
        self.managed = managed

    def translated_title(self, request):
        return translate(self.title, context=request)


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


TYPE_USER = ParticipationType('user', _('user', default="User"), 'participations')
TYPE_INVITATION = ParticipationType('invitation',
                                    _('invitation', default="Invitation"),
                                    'invitations')

PARTICIPATION_TYPES = {
    TYPE_USER.id: TYPE_USER,
    TYPE_INVITATION.id: TYPE_INVITATION,
}

PARTICIPATION_TYPES_BY_PATH_IDENTIFIER = {
    value.path_identifier: value for value in PARTICIPATION_TYPES.values()}


def get_full_user_info(userid=None, member=None):
    if member is None:
        member = api.user.get(userid=userid)

    if userid is None:
        userid = member.getId()

    return PloneUserActor(identifier=userid, user=member).get_label()


def can_manage_member(context, member=None, roles=None):
    if member and member.getId() == api.user.get_current().getId():
        return False
    elif roles and 'WorkspaceOwner' in roles:
        return False
    else:
        return api.user.has_permission(
            'Sharing page: Delegate WorkspaceAdmin role',
            obj=context)


def invitation_to_item(invitation, context):
    if invitation['recipient']:
        recipient_info = get_full_user_info(userid=invitation['recipient'])
    else:
        recipient_info = None

    return dict(name=recipient_info,
                roles=[invitation['role']],
                inviter=get_full_user_info(
                    userid=invitation['inviter']),
                can_manage=can_manage_member(context),
                type_='invitation',
                token=invitation['iid'],
                userid=invitation['recipient'])


def serialize_and_sign_payload(payload):
    """Serialize and sign a payload
    """
    secret = workspace_config.secret
    serializer = URLSafeTimedSerializer(secret)
    return serializer.dumps(payload)


def load_signed_payload(payload):
    secret = workspace_config.secret
    serializer = URLSafeTimedSerializer(secret)
    return serializer.loads(payload)
