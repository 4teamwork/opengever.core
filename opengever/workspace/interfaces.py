from ftw.tabbedview.interfaces import ITabbedviewUploadable
from zope import schema
from zope.interface import Interface


class IWorkspaceRoot(Interface):
    """ Marker interface for Workspace Roots """


class IWorkspace(Interface, ITabbedviewUploadable):
    """ Marker interface for Workspace """


class IWorkspaceFolder(Interface, ITabbedviewUploadable):
    """ Marker interface for Workspace Folders """


class IWorkspaceSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace feature',
        description=u'Whether workspace integration is enabled',
        default=False)

    is_creation_restricted = schema.Bool(
        title=u'Restrict creation',
        description=u'Whether workspace creation is restricted, i.e. only allowed from Gever',
        default=False)

    is_invitation_feature_enabled = schema.Bool(
        title=u'Allow users to be invited to a workspace via email.',
        description=u'This feature allows workspace admins to send email '
                    u'invitations to users. This feature is mainly used to '
                    u'invite external members',
        default=True)

    invitation_group_dn = schema.TextLine(
        title=u'Invitation Group DN',
        description=u'DN of a group where invited users are added on registration',
        default=None,
    )

    videoconferencing_base_url = schema.TextLine(
        title=u'Videoconferencing base URL',
        description=u'Base URL used for default videoconferencing link, '
                    'e.g.: https://meet.jit.si/',
        default=u'https://meet.jit.si/',
        required=False,
    )

    custom_invitation_mail_content = schema.Text(
        title=u'Invitation mail content',
        description=u'Mail content for workspace invitation mails, dynamic '
        'attributes `title`, `user`, `platform` and `accept_url` can be used',
        required=True,
    )


class IWorkspaceMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace meeting feature',
        description=u'Whether workspace meeting integration is enabled',
        default=True)


class IToDoSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable todo feature',
        description=u'Whether todos integration is enabled',
        default=True)


class IToDo(Interface):
    """ Marker interface for ToDos """


class IToDoList(Interface):
    """ Marker interface for ToDo lists"""


class IWorkspaceMeeting(Interface):
    """ Marker interface for Workspace Meetings """


class IWorkspaceMeetingAgendaItem(Interface):
    """ Marker interface for WorkspaceMeetingAgendaItem"""


class IWorkspaceMeetingAttendeesPresenceStateStorage(Interface):
    """Attendees presence state storage adapter.
    """

    def add_or_update(self, userid, state):
        """ Add or update the presence state of the attendee with the given userid
        """

    def delete(self, userid):
        """ Delete the presence state of the attendee with the given userid
        """

    def get_all(self):
        """ Get the presence states of all attendees
        """
