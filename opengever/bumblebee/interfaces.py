from zope import schema
from zope.interface import Interface


class IGeverBumblebeeSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable bumblebee feature',
        description=u'Whether features from opengever.bumblebee are enabled',
        default=False)
