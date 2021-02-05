from zope import schema
from zope.interface import Interface


class IDocugateSettings(Interface):

    is_feature_enabled = schema.Bool(
        title=u'Enable Docugate feature',
        description=u'Whether Docugate integration is enabled. '
                    u'This feature can only be used if Office Connector is activated',
        default=False)
