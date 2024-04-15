from opengever.base.date_time import utcnow_tz_aware
from opengever.base.systemmessages.models import SystemMessage
from opengever.ogds.base.utils import get_current_admin_unit
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from sqlalchemy import and_
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


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
    - return of a 404 Not Found response if that system message doesn't exist
    - retrieval of the respective system messages
    - filter by active, unit id
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
        """Locate a message based on its ID

        Returns:sys_msg: The located message.
        """
        sys_msg = SystemMessage.get(self.msg_id)
        if not sys_msg:
            raise NotFound
        return sys_msg

    def list_messages(self):
        """
        List all messages based on applied filters and ordering.

        Returns:list: A list of all messages that match the applied filters and ordering.
        """
        query = SystemMessage.query
        query = self.extend_with_content_filters(query)
        query = self.extend_with_ordering(query)
        return query.all()

    def extend_with_ordering(self, query):
        """Extend the query with ordering by start date (descending order)."""
        query = query.order_by(SystemMessage.start_ts.desc())
        return query

    def extend_with_content_filters(self, query):
        local_unit_id = get_current_admin_unit().unit_id
        params = self.request.form.copy()
        qs_filters = params.get("filters", {})

        filters = []

        if qs_filters:
            is_active = qs_filters.get('active', False)
            is_current_admin_unit_only = qs_filters.get('current_admin_unit_only', False)

            if is_active:
                filters.append(and_(
                    SystemMessage.start_ts <= utcnow_tz_aware(),
                    utcnow_tz_aware() <= SystemMessage.end_ts
                ))

            if is_current_admin_unit_only:
                filters.append(SystemMessage.admin_unit_id == local_unit_id)

        return query.filter(*filters)
