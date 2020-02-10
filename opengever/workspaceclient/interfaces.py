from zope import schema
from zope.interface import Interface


class IWorkspaceClientSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace client feature',
        description=u'Whether a remote workspace integration is enabled',
        default=False)


class ILinkedWorkspacesMarker(Interface):
    """Marker interface for the ILinkedWorkspaces behavior
    """


class ILinkedWorkspaces(Interface):
    """Behavior interface to manage remote workspaces
    """
