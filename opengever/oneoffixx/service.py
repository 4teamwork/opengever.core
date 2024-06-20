from opengever.api.add import GeverFolderPost
from opengever.officeconnector.helpers import create_oc_url
from opengever.oneoffixx import is_oneoffixx_feature_enabled
from opengever.oneoffixx.interfaces import IOneoffixxSettings
from plone import api
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
import json


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
        # We add a fallback to word templates here so that the API endpoint is not breaking.
        self.filetype = self.request_data.get('filetype', 'GeverWord')
        if isinstance(self.filetype, dict):
            self.filetype = self.filetype['token']

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

    def before_deserialization(self, obj):
        filetype_tag_mapping = json.loads(
            api.portal.get_registry_record(
                interface=IOneoffixxSettings, name="filetype_tag_mapping"))
        filetype = [item for item in filetype_tag_mapping if item['tag'] == self.filetype][0]

        annotations = IAnnotations(obj)
        annotations["tag"] = filetype['tag']
        annotations["filename"] = u'oneoffixx_from_template.{}'.format(filetype['extension'])
