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


class IToDo(Interface):
    """ Marker interface for ToDos """


class IToDoList(Interface):
    """ Marker interface for ToDo lists"""
