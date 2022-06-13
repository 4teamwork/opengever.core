from zope import schema
from zope.interface import Interface
import re


EMAIL_REGEX = re.compile('^[^@]+@[^@]+$')


def valid_email(value):
    """Very basic email "validator" that makes sure there is an `@` sign
    preceded and followed by at least one char.

    Everything else is validated by actually sending the mail.
    """
    return EMAIL_REGEX.match(value)


class IWorkspaceInvitationSchema(Interface):

    recipient_email = schema.TextLine(
        title=u'Recipient Email',
        description=u'Email of the recipient.',
        constraint=valid_email)

    role = schema.Choice(
        title=u'Role',
        description=u'Role of this invitation.',
        vocabulary='opengever.workspace.RolesVocabulary',
        required=True)

    comment = schema.Text(
        title=u'Comment',
        description=u'Comment to this invitation.',
        required=False,
        missing_value=u'',
        default=u'',
    )
