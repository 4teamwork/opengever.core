from zope import schema
from zope.interface import Interface


class IOfficeatworkSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable officeatwork feature',
        description=u'Whether officeatwork integration is enabled',
        default=False)
