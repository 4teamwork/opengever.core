from opengever.api.add import GeverFolderPost
from opengever.officeconnector.helpers import create_oc_url
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.oneoffixx.api_client import OneoffixxAPIClient
from opengever.oneoffixx.templates import get_whitelisted_oneoffixx_templates
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations


class CreateDocumentFromOneOffixxTemplate(GeverFolderPost):
    """API Endpoint to create a document from a OneOffixx template.

    The document is created in the shadow state and the endpoint returns the
    @id of the newly created document and the OfficeConnector URL.
    """
    def reply(self):
        if not is_oneoffixx_feature_enabled():
            raise NotFound
        return super(CreateDocumentFromOneOffixxTemplate, self).reply()

    def extract_data(self):
        self.type_ = 'opengever.document.document'
        self.id_ = None
        self.data = self.request_data.get('document', {})
        self.title_ = self.data.get('title', None)

        template_id = self.request_data.get('template_id')

        if not template_id:
            raise BadRequest("Property 'template_id' is required.")

        self.template = self.lookup_template(template_id)

        if not self.template:
            raise BadRequest('The requested template_id does not exist.')

    def lookup_template(self, template_id):
        api_client = OneoffixxAPIClient()
        templates_by_id = {
            template.template_id: template for template
            in get_whitelisted_oneoffixx_templates(api_client)
        }
        return templates_by_id.get(template_id, None)

    def before_deserialization(self, obj):
        annotations = IAnnotations(obj)
        annotations["template-id"] = self.template.template_id
        annotations["languages"] = self.template.languages
        annotations["filename"] = self.template.filename
        annotations["content-type"] = self.template.content_type

    def add_object_to_context(self):
        super(CreateDocumentFromOneOffixxTemplate, self).add_object_to_context()

        # The workflow needs to be set after the object has been added to the
        # context. If we do it earlier, it will reset the state if we add the
        # object to a context providing a placeful workflow. This is the case
        # if we add it i.e. to a private dossier, inbox or workspace.
        self.obj.as_shadow_document()

    def serialize_object(self):
        return {
            '@id': self.obj.absolute_url(),
            'url': create_oc_url(
                self.request, self.obj, dict(action='oneoffixx'),),
        }
