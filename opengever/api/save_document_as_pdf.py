from opengever.document.behaviors import IBaseDocument
from opengever.document.browser.save_pdf_document_under import trigger_conversion
from opengever.document.forms import create_destination_document
from opengever.document.forms import is_version_convertable
from opengever.document.versioner import Versioner
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.interface import alsoProvides


class SaveDocumentAsPdfPost(Service):

    def get_document(self, data):
        uid = data.get('document_uid', None)
        if not uid:
            return
        catalog = api.portal.get_tool('portal_catalog')
        brain = catalog(UID=uid, object_provides=[IBaseDocument.__identifier__])
        if brain:
            return brain[0].getObject()

    def reply(self):
        # Disable CSRF protection
        alsoProvides(self.request, IDisableCSRFProtection)

        data = json_body(self.request)
        document = self.get_document(data)
        if not document:
            raise BadRequest(
                "Property 'document_uid' is required and should be a UID of a document")

        if is_restricted_workspace_and_guest(document):
            raise Forbidden()

        version_id = data.get('version_id', None)
        if version_id and not isinstance(version_id, int):
            raise BadRequest("Property 'version_id' should be an integer.")
        if version_id == 0 and not Versioner(document).has_initial_version():
            version_id = None

        if not is_version_convertable(document, self.request, version_id):
            raise BadRequest("This document is not convertable.")

        destination_document = create_destination_document(
            document, self.request, version_id, self.context)
        trigger_conversion(document, destination_document, version_id)

        self.request.response.setHeader("Location", destination_document.absolute_url())
        self.reply_no_content(201)
