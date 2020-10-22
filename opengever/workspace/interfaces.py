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


class IToDo(Interface):
    """ Marker interface for ToDos """


class IToDoList(Interface):
    """ Marker interface for ToDo lists"""


class IWorkspaceMeeting(Interface):
    """ Marker interface for Workspace Meetings """
