from zope import schema
from zope.interface import Interface


class IWorkspaceClientSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable workspace client feature',
        description=u'Whether a remote workspace integration is enabled',
        default=False)
