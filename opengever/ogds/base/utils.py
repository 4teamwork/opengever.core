from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from z3c.saconfig import named_scoped_session
from opengever.ogds.base.model.client import Client
from opengever.ogds.base.interfaces import IClientConfiguration


Session = named_scoped_session('opengever.ogds')


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """

    return Session()


def get_current_client():
    """Returns the current client.
    """

    session = create_session()
    client_id = get_client_id()

    clients = session.query(Client).filter_by(client_id=client_id).all()
    if len(clients) == 0:
        raise ValueError('Current client not found')
    else:
        return clients[0]

def get_client_id():
    """Returns the client_id of the current client.
    """

    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IClientConfiguration)
    return proxy.client_id
