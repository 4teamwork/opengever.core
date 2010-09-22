from zope import schema
from zope.interface import Interface


class IUser(Interface):
    """Marker interface for users.
    """


class IClient(Interface):
    """Marker interface for clients.
    """


class IClientConfiguration(Interface):
    """p.a.registry interface for configuring a client
    """

    client_id = schema.TextLine(title=u'Client ID')


class IContactInformation(Interface):
    """Contact information utility interface.
    """


class IClientCommunicator(Interface):
    """Utility interface for the client communicator.
    """
