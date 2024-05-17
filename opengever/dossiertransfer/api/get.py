from ftw.mail.mail import IMail
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.security import elevated_privileges
from opengever.document.behaviors import IBaseDocument
from opengever.dossiertransfer.api.base import DossierTransferLocator
from plone import api
from plone.namedfile.utils import stream_data
from plone.restapi.services import _no_content_marker
from zExceptions import NotFound
from zExceptions.unauthorized import Unauthorized
import json


class DossierTransfersGet(DossierTransferLocator):
    """API Endpoint that returns DossierTransfers.

    GET /@dossier-transfers/42 HTTP/1.1
    GET /@dossier-transfers HTTP/1.1
    GET /@dossier-transfers/blob/<document-UID> HTTP/1.1
    """

    def render(self):
        self.check_permission()
        content = self.reply()

        # Exception for blob download: Do not attempt to JSON serialize
        # blob download responses. Instead directly return the
        # IStreamIterator and let ZPublisher handle it.
        if self.is_blob_request():
            return content

        if content is not _no_content_marker:
            self.request.response.setHeader("Content-Type", self.content_type)
            return json.dumps(
                content, indent=2, sort_keys=True, separators=(", ", ": ")
            )

    def check_permission(self):
        if self.has_valid_token():
            # Server-to-server requests to fetch the full transfer contents are
            # performed anonymously, but with a valid token that matches a
            # particular transfer. We must not restrict these.
            return

        return super(DossierTransfersGet, self).check_permission()

    def reply(self):
        if self.transfer_id and len(self.params) == 1:
            # Get transfer by id
            transfer = self.locate_transfer()
            if self.full_content_requested():
                # Get full content required to perform a transfer
                if not self.has_valid_token():
                    raise Unauthorized(
                        "full_content requires a valid transfer token")
                return self.serialize(transfer, full_content=True)
            return self.serialize(transfer)

        elif self.is_blob_request():
            return self.stream_document_blob()

        if len(self.params) == 0:
            # List all transfers
            return self.list()
        else:
            raise NotFound

    def list(self):
        transfers = self.list_transfers()
        result = {
            '@id': '/'.join((api.portal.get().absolute_url(), '@dossier-transfers')),
            'items': [self.serialize(t) for t in transfers],
        }
        return result

    def full_content_requested(self):
        return bool(self.request.form.get('full_content', False))

    def stream_document_blob(self):
        transfer = self.locate_transfer()
        document_uid = self.params[2]

        with elevated_privileges():
            root_dossier = api.content.uuidToObject(transfer.root)
            catalog = api.portal.get_tool('portal_catalog')

            query = {
                'path': '/'.join(root_dossier.getPhysicalPath()),
                'object_provides': IBaseDocument.__identifier__,
                'UID': document_uid,
            }
            brains = catalog.unrestrictedSearchResults(**query)

            if len(brains) == 0:
                raise NotFound

            if not transfer.all_documents:
                if document_uid not in transfer.documents:
                    raise Unauthorized

            document = brains[0].getObject()

            if IMail.providedBy(document):
                namedfile = document.message
            else:
                namedfile = document.file

        filename = getattr(namedfile, 'filename', u'document.bin').encode('utf-8')
        set_attachment_content_disposition(self.request, filename, namedfile)
        return stream_data(namedfile)
