from Products.Five import BrowserView
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from zope.component import getUtility
from zope.interface import Interface


current_client_marker = object()


class IOpengeverView(Interface):
    """Interface for the opengever_view which allows the defined
    methods to be traversed.
    """

    def client_id():
        pass

    def is_user_assigned_to_client():
        pass


class OpengeverView(BrowserView):
    """The opengever_view provides various information about state and
    configuration of the current opengever client.
    """

    def render(self):
        return ''

    def client_id(self):
        """Returns the client id (string) of this client.
        """
        return get_client_id()

    def is_user_assigned_to_client(self, client_id=None):
        """Returns `True` if the authenticated user is assigned to
        this client.
        """

        info = getUtility(IContactInformation)
        if not client_id:
            client_id = get_client_id()

        return info.is_client_assigned(client_id=client_id)
