from opengever.base.model import create_session
from opengever.dossiertransfer.api.base import DossierTransferLocator


class DossierTransfersDelete(DossierTransferLocator):
    """API Endpoint that deletes a DossierTransfer.

    DELETE /@dossier-transfers/42 HTTP/1.1
    """

    def reply(self):
        transfer = self.locate_transfer()
        session = create_session()
        session.delete(transfer)
        return self.reply_no_content()
