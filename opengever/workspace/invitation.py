from opengever.workspace.participation import PARTICIPATION_ROLES
from zope import schema
from zope.interface import Interface


class IWorkspaceInvitationSchema(Interface):

    recipient_email = schema.TextLine(
        title=u'Recipient Email',
        description=u'Email the recipient.')

    role = schema.Choice(
        title=u'Role',
        description=u'Role of this invitation.',
        values=PARTICIPATION_ROLES.keys(),
        required=True)
