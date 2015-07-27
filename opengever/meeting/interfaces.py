from zope import schema
from zope.interface import Interface


class IMeetingSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable meeting feature',
        description=u'Whether features from opengever.meeting are enabled',
        default=False)


class ISQLLockable(Interface):
    """Marker interface for lockable sql objects or wrapper(objects)."""


class IMeetingWrapper(Interface):
    """Marker interface for meeting object wrappers."""
