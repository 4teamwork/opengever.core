from opengever.api.add import FolderPost
from opengever.docugate import is_docugate_feature_enabled
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.service import OfficeConnectorPayload
from opengever.officeconnector.service import OfficeConnectorURL
from plone import api
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.interface import alsoProvides
import json


class OfficeConnectorDocugateURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'docugate' action payload for
    this document.
    """

    def render(self):
        if is_docugate_feature_enabled():
            payload = {'action': 'docugate'}

            return self.create_officeconnector_url_json(payload)

        # Fail per default
        raise NotFound


class OfficeConnectorDocugatePayload(OfficeConnectorPayload):
    """Issue JSON instruction payloads for OfficeConnector.

    Contains the instruction set to generate a document from a docugate
    template (Docugate-XML), then checkout the corresponding document (checkout-url)
    to open the created document in an editor. From there the normal checkout,
    checkin cycle can begin.
    """

    @staticmethod
    def document_is_valid(document):
        return (
            IDocumentFromDocugate.providedBy(document)
            and document.is_shadow_document()
        )

    def render(self):
        payloads = self.get_base_payloads()

        for payload in payloads:
            # A permission check to verify the user is also able to upload
            authorized = api.user.has_permission(
                'Modify portal content',
                obj=payload['document'],
            )

            if authorized:
                del payload['document']
                payload['docugate-xml'] = '@@docugate-xml'

            else:
                # Fail per default
                raise Forbidden

        self.request.response.setHeader('Content-type', 'application/json')

        return json.dumps(payloads)


class CreateDocumentFromDocugateTemplate(FolderPost):
    """API Endpoint to create a document from a Docugate template
    """

    def extract_data(self):
        self.type_ = 'opengever.document.document'
        self.id_ = None
        self.title_ = self.request_data.get("title", None)

    def before_deserialization(self, obj):
        alsoProvides(obj, IDocumentFromDocugate)

    def add_object_to_context(self):
        super(CreateDocumentFromDocugateTemplate, self).add_object_to_context()

        # The workflow needs to be set after the object has been added to the
        # context. If we do it earlier, it will reset the state if we add the
        # object to a context providing a placeful workflow. This is the case
        # if we add it i.e. to a private dossier, inbox or workspace.
        self.obj.as_shadow_document()

    def serialize_object(self):
        return {
            '@id': self.obj.absolute_url(),
            'url': create_oc_url(
                self.request, self.obj, dict(action='docugate'),),
        }
