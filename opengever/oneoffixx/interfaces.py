from zope import schema
from zope.interface import Interface


class IOneoffixxSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable OneOffixx feature',
        description=u'Whether OneOffixx integration is enabled. '
                    'This feature can only be used if officeconnector is activated',
        default=False)
