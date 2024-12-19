from AccessControl import Unauthorized
from opengever.document.document import Document
from opengever.sign.sign import Signer
from opengever.sign.token import InvalidToken
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden


class UploadSignedPdfPost(Service):
    """Endpoint for uploading a signed pdf to a document and completing the
    sign process"""

    def __call__(self):
        if api.content.get_state(obj=self.context) != Document.signing_state:
            raise Forbidden()

        self.extract_payload()
        self.signer = Signer(self.context)

        return super(UploadSignedPdfPost, self).__call__()

    def reply(self):
        with self.signer.adopt_issuer():
            self.signer.complete_signing(self.signed_pdf_data)
        self.signer.invalidate_token()
        self.request.response.setStatus(201)
        return super(UploadSignedPdfPost, self).reply()

    def check_permission(self):
        try:
            self.signer.validate_token(self.access_token)
        except InvalidToken:
            raise Unauthorized()

    def extract_payload(self):
        data = json_body(self.request)
        access_token = data.get('access_token')
        if not access_token:
            raise BadRequest("Property 'access_token' is required")

        signed_pdf_data = data.get('signed_pdf_data')
        if not signed_pdf_data:
            raise BadRequest("Property 'signed_pdf_data' is required")

        self.access_token = access_token
        self.signed_pdf_data = signed_pdf_data


class UpdatePendingSigningJob(Service):
    """Endpoint for updating metadata for a pending signing job"""

    def __call__(self):
        if api.content.get_state(obj=self.context) != Document.signing_state:
            raise Forbidden()

        self.extract_payload()
        self.signer = Signer(self.context)

        return super(UpdatePendingSigningJob, self).__call__()

    def reply(self):
        with self.signer.adopt_issuer():
            self.signer.update_pending_signing_job(**self.data)

        self.request.response.setStatus(200)
        return self.signer.serialize_pending_signing_job()

    def check_permission(self):
        try:
            self.signer.validate_token(self.access_token)
        except InvalidToken:
            raise Unauthorized()

    def extract_payload(self):
        data = json_body(self.request)
        access_token = data.get('access_token')
        if not access_token:
            raise BadRequest("Property 'access_token' is required")

        data = data.get('signature_data')
        if not data:
            raise BadRequest("Property 'signature_data' is required")

        self.access_token = access_token
        self.data = {
            'signers': data.get('signers'),
            'editors': data.get('editors'),
        }
