from zope import schema
from zope.interface import Interface


class IRisSettings(Interface):

    base_url = schema.TextLine(
        title=u'Base URL for Ris',
        description=u'Implicitly used as Ris feature flag'
    )
