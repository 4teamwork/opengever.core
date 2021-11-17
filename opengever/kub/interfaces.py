from zope import schema
from zope.interface import Interface


class IKuBSettings(Interface):

    base_url = schema.TextLine(
        title=u'Base URL for KuB',
        description=u'Implicitly used as KUB feature flag')

    service_token = schema.TextLine(
        title=u'KuB Service token',
        description=u'Authentication service token for the KuB service.')
