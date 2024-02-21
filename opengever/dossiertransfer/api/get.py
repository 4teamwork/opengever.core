from opengever.dossiertransfer.api.base import DossierTransferLocator
from plone import api


class DossierTransfersGet(DossierTransferLocator):
    """API Endpoint that returns DossierTransfers.

    GET /@dossier-transfers/42 HTTP/1.1
    GET /@dossier-transfers HTTP/1.1
    """

    def reply(self):
        if self.transfer_id:
            # Get transfer by id
            transfer = self.locate_transfer()
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
