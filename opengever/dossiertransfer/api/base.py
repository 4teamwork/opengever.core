from opengever.dossiertransfer import is_dossier_transfer_feature_enabled
from opengever.dossiertransfer.model import DossierTransfer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import NotFound
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

    def locate_transfer(self):
        transfer_id = self.transfer_id
        if transfer_id is not None:
            transfer = DossierTransfer.get(transfer_id)
            if not transfer:
                raise NotFound

            return transfer
