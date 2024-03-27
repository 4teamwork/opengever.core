from datetime import datetime
from datetime import timedelta
from opengever.base.systemmessages.models import SystemMessages
from opengever.ogds.base.utils import get_current_admin_unit
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import pytz


class SystemMessagesBase(Service):
    """Base service class for all @system-messages endpoints.
    """

    def render(self):
        return super(SystemMessagesBase, self).render()

    def serialize(self, sys_msg):
        return getMultiAdapter((sys_msg, getRequest()), ISerializeToJson)()


@implementer(IPublishTraverse)
class SystemMessageLocator(SystemMessagesBase):
    """Locates a SystemMessage by its ID.

    This is a Service base class for all services that need to look up a
    system messages via a /@system-messages/{msg_id} style URL.

    It handles
    - extraction of the {msg_id} path parameter
    - error response for incorrect number of path parameters
    - validation of {msg_id} as an integer (and error response)
    - return of a 404 Not Found response if that transfer doesn't exist
    - retrieval of the respective system messages
    - filter by active (when the end ts > yesterday)
    - filter by admin unit

    in a single place so that not every service has to implement this again,
    and we ensure consistent behavior across all services.

    Because the GET service supports both individual retrieval as well as
    listing, this needs to be handled here as well.
    """

    def __init__(self, context, request):
        super(SystemMessageLocator, self).__init__(context, request)
        self.params = []
        self.msg_id = None

    def __call__(self):
        self.msg_id = self._extract_msg_id()
        return super(SystemMessageLocator, self).__call__()

    def publishTraverse(self, request, name):
        # Consume any path segments after /system-messages as parameters
        self.params.append(name)
        return self

    def _extract_msg_id(self):
        # We'll accept zero (listing) or one (get by id) params, but not more
        if len(self.params) > 1:
            raise BadRequest(
                'Must supply either exactly one {msg_id} path parameter '
                'to fetch a specific message, or no parameter for a '
                'listing of all system messages.')

        # We have a valid number of parameters for the given endpoint
        if len(self.params) == 1:
            try:
                msg_id = int(self.params[0])
            except ValueError:
                raise BadRequest('{msg_id} path parameter must be an integer')
            return msg_id

    def locate_message(self):
        """Locate a message based on its ID.

        Raises:
            NotFound: If the message with the given ID is not found.
            Unauthorized: If the message exists but the user is not authorized to access it.

        Returns:
            sys_msg: The located message.
        """
        msg_id = self.msg_id
        # Check if the message with the given ID exists in the SystemMessages
        if not SystemMessages.get(msg_id):
            # If not found, raise NotFound exception
            raise NotFound

        query = SystemMessages.query
        query = query.filter(SystemMessages.id == msg_id)
        # Get the first result from the query
        sys_msg = query.first()

        # If no message found, raise Unauthorized exception
        if not sys_msg:
            raise Unauthorized

        # Return the located message
        return sys_msg

    def list_messages(self):
        """List all messages based on applied filters and ordering.

        Returns:
            list: A list of all messages that match the applied filters and ordering.
        """
        query = SystemMessages.query
        query = self.extend_with_content_filters(query)
        query = self.extend_with_ordering(query)
        return query.all()

    def extend_with_ordering(self, query):
        """Extend the query with ordering by start date (descending order)."""
        query = query.order_by(SystemMessages.start.desc())
        return query

    def extend_with_content_filters(self, query):
        """Extend the query with content filters.

        Args:
            query (Query): The query object to extend with filters.

        Returns:
            Query: The extended query object.
        """
        local_unit_id = get_current_admin_unit().unit_id
        # Get form parameters from the request
        params = self.request.form.copy()
        filters = []

        is_active = params.get('active', False)
        is_current_admin_unit_only = params.get('current_admin_unit_only', False)

        if is_active:
            # Calculate yesterday's date
            yesterday = datetime.now(pytz.utc) - timedelta(days=1)
            # Add filter for messages that end after yesterday
            filters.append(SystemMessages.end > yesterday)

        if is_current_admin_unit_only:
            # Add filter for messages belonging to the current admin unit
            filters.append(SystemMessages.admin_unit_id == local_unit_id)

        return query.filter(*filters)
