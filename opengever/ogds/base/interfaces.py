from zope import schema
from zope.interface import Interface


class IClientConfiguration(Interface):
    """p.a.registry interface for configuring a client
    """
    
    client_id = schema.TextLine(title=u'Client ID')
