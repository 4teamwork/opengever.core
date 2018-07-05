from opengever.base.request import tracebackify
from opengever.base.utils import ok_response
from opengever.meeting.connector.connector import Connector
from Products.Five import BrowserView


@tracebackify
class ReceiveConnectorAction(BrowserView):
    """Receives a connector action and passes the context and the request
    back to the connector.

    This view is only available for internal requests.
    """

    def __call__(self):
        Connector.receive(self.context, self.request)
        return ok_response(self.request)
