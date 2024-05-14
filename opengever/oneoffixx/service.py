from opengever.api.add import GeverFolderPost
from opengever.officeconnector.helpers import create_oc_url
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from zExceptions import NotFound


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
