from opengever.dossiertransfer import is_dossier_transfer_feature_enabled
from opengever.dossiertransfer.model import DossierTransfer
from opengever.dossiertransfer.model import TRANSFER_STATE_COMPLETED
from opengever.dossiertransfer.model import TRANSFER_STATE_PENDING
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from sqlalchemy import case
from sqlalchemy import or_
from zExceptions import BadRequest
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


class DossierTransfersBase(Service):
    """Base service class for all @dossier-transfer endpoints.
    """

    def render(self):
        if not is_dossier_transfer_feature_enabled():
            raise BadRequest("Feature 'dossier_transfers' is not enabled.")
        return super(DossierTransfersBase, self).render()

    def serialize(self, transfer):
        return getMultiAdapter((transfer, getRequest()), ISerializeToJson)()


@implementer(IPublishTraverse)
class DossierTransferLocator(DossierTransfersBase):
    """Locates a DossierTransfer by its ID.

    This is a Service base class for all services that need to look up a
    dossier transfer via a /@dossier-transfers/{transfer_id} style URL.

    It handles
    - extraction of the {transfer_id} path parameter
    - error response for incorrect number of path parameters
    - validation of {transfer_id} as an integer (and error response)
    - return of a 404 Not Found response if that transfer doesn't exist
    - retrieval of the respective dossier transfer

    in a single place so that not every service has to implement this again,
    and we ensure consistent behavior across all services.

    Because the GET service supports both individual retrieval as well as
    listing, this needs to be handled here as well.
    """

    def __init__(self, context, request):
        super(DossierTransferLocator, self).__init__(context, request)
        self.params = []
        self.transfer_id = None

    def __call__(self):
        self.transfer_id = self._extract_transfer_id()
        return super(DossierTransferLocator, self).__call__()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@dossier-transfers as parameters
        self.params.append(name)
        return self

    def has_valid_token(self):
        transfer_id = self._extract_transfer_id()
        transfer = DossierTransfer.get(transfer_id)
        if transfer:
            token = self.request.getHeader('X-GEVER-Dossier-Transfer-Token')
            return transfer.is_valid_token(token)
        return False

    def _extract_transfer_id(self):
        # We'll accept zero (listing) or one (get by id) params, but not more
        if len(self.params) > 1:
            raise BadRequest(
                'Must supply either exactly one {transfer_id} path parameter '
                'to fetch a specific transfer, or no parameter for a '
                'listing of all transfers.')

        # We have a valid number of parameters for the given endpoint
        if len(self.params) == 1:
            try:
                transfer_id = int(self.params[0])
            except ValueError:
                raise BadRequest('{transfer_id} path parameter must be an integer')
            return transfer_id

    def _is_inbox_user(self, user_id):
        ogds_user = ogds_service().fetch_user(user_id)
        local_unit = get_current_admin_unit()
        for org_unit in local_unit.org_units:
            if ogds_user in org_unit.inbox_group.users:
                return True
        return False

    def locate_transfer(self):
        transfer_id = self.transfer_id
        if not DossierTransfer.get(transfer_id):
            # Distinguish 404 from 401
            raise NotFound

        query = DossierTransfer.query
        query = query.filter(DossierTransfer.id == transfer_id)
        query = self.extend_with_security_filters(query)
        transfer = query.first()

        if not transfer:
            raise Unauthorized

        return transfer

    def list_transfers(self):
        query = DossierTransfer.query
        query = self.extend_with_security_filters(query)
        query = self.extend_with_content_filters(query)
        query = self.extend_with_ordering(query)
        return query.all()

    def extend_with_security_filters(self, query):
        current_user = api.user.get_current()
        if current_user.has_role('Manager'):
            # Managers may always list or fetch any transfer
            return query

        user_id = current_user.getId()
        local_unit_id = get_current_admin_unit().unit_id

        # Nobody may see transfers where the current admin unit is not involved
        filters = [or_(
            DossierTransfer.source_id == local_unit_id,
            DossierTransfer.target_id == local_unit_id,
        )]

        if self.has_valid_token():
            # Server-to-server requests to fetch the full transfer contents are
            # performed anonymously, but with a valid token that matches a
            # particular transfer. We must not restrict these.
            return query.filter(*filters)

        if not self._is_inbox_user(user_id):
            # Only inbox users may see transfers other than their own
            filters.append(DossierTransfer.source_user_id == user_id)

        return query.filter(*filters)

    def extend_with_content_filters(self, query):
        local_unit_id = get_current_admin_unit().unit_id
        params = self.request.form.copy()
        filters = []

        # Direction
        direction = params.get('direction')

        if direction == 'incoming':
            filters.append(DossierTransfer.target_id == local_unit_id)

        elif direction == 'outgoing':
            filters.append(DossierTransfer.source_id == local_unit_id)

        # States
        states = params.get('states', [])
        if states:
            filters.append(
                or_(*[DossierTransfer.state == state for state in states]))

        return query.filter(*filters)

    def extend_with_ordering(self, query):
        return query.order_by(
            case([
                (DossierTransfer.state == TRANSFER_STATE_PENDING, 0),
                (DossierTransfer.state == TRANSFER_STATE_COMPLETED, 1),
            ], else_=99),
            DossierTransfer.created.desc(),
            DossierTransfer.id,
        )
