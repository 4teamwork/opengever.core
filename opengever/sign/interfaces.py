from zope import schema
from zope.interface import Interface


class ISignSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable sign feature',
        description=u'Whether sign feature is enabled',
        default=False)
