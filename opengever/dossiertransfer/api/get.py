from opengever.dossiertransfer.api.base import DossierTransferLocator
from opengever.dossiertransfer.model import DossierTransfer
from plone import api


class DossierTransfersGet(DossierTransferLocator):
    """API Endpoint that returns DossierTransfers.

    GET /@dossier-transfers/42 HTTP/1.1
    GET /@dossier-transfers HTTP/1.1
    """

    def reply(self):
        transfer = self.locate_transfer()
        if transfer is not None:
            # Get transfer by id
            return self.serialize(transfer)
        else:
            # List all transfers
            return self.list()

    def list(self):
        transfers = DossierTransfer.query.all()
        result = {
            '@id': '/'.join((api.portal.get().absolute_url(), '@dossier-transfers')),
            'items': [self.serialize(t) for t in transfers],
        }
        return result
