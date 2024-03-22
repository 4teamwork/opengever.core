from opengever.dossiertransfer.api.base import DossierTransferLocator
from plone import api
from zExceptions.unauthorized import Unauthorized


class DossierTransfersGet(DossierTransferLocator):
    """API Endpoint that returns DossierTransfers.

    GET /@dossier-transfers/42 HTTP/1.1
    GET /@dossier-transfers HTTP/1.1
    """

    def check_permission(self):
        if self.has_valid_token():
            # Server-to-server requests to fetch the full transfer contents are
            # performed anonymously, but with a valid token that matches a
            # particular transfer. We must not restrict these.
            return

        return super(DossierTransfersGet, self).check_permission()

    def reply(self):
        if self.transfer_id:
            # Get transfer by id
            transfer = self.locate_transfer()
            if self.full_content_requested():
                # Get full content required to perform a transfer
                if not self.has_valid_token():
                    raise Unauthorized(
                        "full_content requires a valid transfer token")
                return self.serialize(transfer, full_content=True)
            return self.serialize(transfer)

        # List all transfers
        return self.list()

    def list(self):
        transfers = self.list_transfers()
        result = {
            '@id': '/'.join((api.portal.get().absolute_url(), '@dossier-transfers')),
            'items': [self.serialize(t) for t in transfers],
        }
        return result

    def full_content_requested(self):
        return bool(self.request.form.get('full_content', False))
