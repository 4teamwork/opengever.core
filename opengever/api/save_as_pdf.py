from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.base.command import CreateDocumentCommand
from opengever.document import _
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_OWNER_ID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_UUID_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_SOURCE_VERSION_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_STATUS_KEY
from opengever.document.browser.save_pdf_document_under import PDF_SAVE_TOKEN_KEY
from opengever.document.interfaces import IDocumentSavedAsPDFMarker
from opengever.document.versioner import Versioner
from plone import api
from plone.dexterity.utils import iterSchemataForType
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.uuid.interfaces import IUUID
from uuid import uuid4
from z3c.relationfield.relation import RelationValue
from zExceptions import BadRequest
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder


class SaveAsPdf(Service):
    """Create a pdf representation of the current document version and save it to
    the same folder """

    def get_callback_url(self):
        return "{}/save_pdf_under_callback".format(
            self.destination_document.absolute_url())

    def reply(self):
        body = json_body(self.request)
        self.version_id = body["version_id"]

        self.destination = self.context.get_parent_dossier()
        self.destination_document = self.create_destination_document()
        self.source_document = self.context

        # copied from save_pdf_document_under
        token = str(uuid4())
        annotations = IAnnotations(self.destination_document)
        annotations[PDF_SAVE_TOKEN_KEY] = token
        annotations[PDF_SAVE_OWNER_ID_KEY] = api.user.get_current().getId()

        if self.version_id is not None:
            document = Versioner(self.source_document).retrieve(self.version_id)
        else:
            document = self.source_document

        import pdb; pdb.set_trace()
        if IBumblebeeServiceV3(getRequest()).queue_demand(
                document, PROCESSING_QUEUE, self.get_callback_url(), opaque_id=token):
            annotations[PDF_SAVE_STATUS_KEY] = "conversion-demanded"
        else:
            raise BadRequest("This document is not convertable.")

        self.request.response.setStatus(204)
        return super(SaveAsPdf, self).reply()

    def create_destination_document(self):
        # get all the metadata that will be set on the created file.
        # We blacklist some fields that should not be copied
        fields_to_skip = set(("file",
                              "archival_file",
                              "archival_file_state",
                              "thumbnail",
                              "preview",
                              "digitally_available",
                              "changeNote",
                              "changed",
                              "relatedItems",))
        metadata = {}
        for schema in iterSchemataForType(self.context.portal_type):
            for name, schema_field in getFieldsInOrder(schema):
                if name in fields_to_skip:
                    continue
                field_instance = schema_field.bind(self.context)
                metadata[name] = field_instance.get(field_instance.interface(self.context))
        command = CreateDocumentCommand(self.destination, None, None, **metadata)
        destination_document = command.execute()

        # We make it in shadow state until its file is set by the callback view
        destination_document.as_shadow_document()
        # Add marker interface. This should be useful in the future for
        # cleanup jobs, retries if the PDF was not delivered and so on.
        alsoProvides(destination_document, IDocumentSavedAsPDFMarker)
        # Add annotations needed for the SavePDFDocumentUnder view.
        annotations = IAnnotations(destination_document)
        annotations[PDF_SAVE_SOURCE_UUID_KEY] = IUUID(self.context)
        annotations[PDF_SAVE_SOURCE_VERSION_KEY] = self.version_id

        # The missing_value attribute of a z3c-form field is used
        # as soon as an object has no default_value i.e. after creating
        # an object trough the command-line.
        #
        # Because the relatedItems field needs a list as a missing_value,
        # we will fall into the "mutable keyword argument"-python gotcha.
        # The relatedItems will be shared between the object-instances.
        #
        # Unfortunately the z3c-form field does not provide a
        # missing_value-factory (like the defaultFactory) which would be
        # necessary to fix this issue properly.
        #
        # As a workaround we make sure that the new document's relatedItems
        # is different object from the source document's.
        IRelatedDocuments(destination_document).relatedItems = list(
            IRelatedDocuments(destination_document).relatedItems)

        IRelatedDocuments(destination_document).relatedItems.append(
            RelationValue(getUtility(IIntIds).getId(self.context)))

        msg = _(u'Document ${document} was successfully created in ${destination}',
                mapping={"document": destination_document.title, "destination": self.destination.title})
        api.portal.show_message(msg, self.request, type='info')

        return destination_document
