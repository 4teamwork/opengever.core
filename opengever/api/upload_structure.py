from opengever.document.document import is_email_upload
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.private.interfaces import IPrivateContainer
from opengever.workspace.utils import is_within_workspace
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest


class UploadStructurePost(Service):
    """API Endpoint to check the structure of an upload. It takes a mandatory
    list of 'files' as input, deduces and returns the list of containers
    and documents / mails that will need to be created to reproduce the
    file hierarchy being uploaded.

    POST /@upload-structure HTTP/1.1
    {
        "files": ["folder1/file1.txt", "folder1/folder2/file2.eml"]
    }
    """

    mail_type = 'ftw.mail.mail'
    document_type = 'opengever.document.document'

    def __init__(self, context, request):
        super(UploadStructurePost, self).__init__(context, request)
        if is_within_workspace(self.context):
            self.container_type = 'opengever.workspace.folder'
        elif IPrivateContainer.providedBy(context):
            self.container_type = 'opengever.private.dossier'
        else:
            self.container_type = 'opengever.dossier.businesscasedossier'

    def container(self, relative_path):
        return {'@type': self.container_type,
                'relative_path': relative_path,
                'items': {}}

    def file(self, relative_path, filename):
        if is_email_upload(filename):
            return {'@type': self.mail_type,
                    'relative_path': relative_path}
        return {'@type': self.document_type,
                'relative_path': relative_path}

    def extract_data(self):
        data = json_body(self.request)
        files = data.get("files", None)
        if not files:
            raise BadRequest("Property 'files' is required")
        for file in files:
            if not file:
                raise BadRequest("Empty filename not supported")
        return files

    def check_permission(self):
        if not api.user.has_permission('Add portal content', obj=self.context):
            raise BadRequest("User is not allowed to add objects here")

    def extract_structure(self, files):
        root = {'items': {}}
        max_depth = 0
        items_total = 0
        for path in sorted(files):
            curr_depth = 0
            segments = path.split("/")
            parent = root
            for i, segment in enumerate(segments[:-1]):
                relative_path = "/".join(segments[:i+1])
                if not segment:
                    continue
                curr_depth += 1
                if segment not in parent['items']:
                    parent['items'][segment] = self.container(
                        relative_path)
                    items_total += 1
                child = parent['items'][segment]
                if 'items' not in child:
                    raise BadRequest("Name conflict")
                parent = child
            parent['items'][segments[-1]] = self.file(
                path, segments[-1])
            items_total += 1
            max_depth = max(max_depth, curr_depth)
        root['max_container_depth'] = max_depth
        root['items_total'] = items_total
        return root

    def _is_dossier(self):
        return IDossierMarker.providedBy(self.context)

    def check_dossier_depth(self, structure):
        if self._is_dossier():
            current_depth = self.context._get_dossier_depth()
        else:
            current_depth = 0

        max_depth = api.portal.get_registry_record(
            name='maximum_dossier_depth',
            interface=IDossierContainerTypes
            )
        if current_depth + structure["max_container_depth"] > max_depth + 1:
            raise BadRequest("Maximum dossier depth exceeded")

    def check_addable(self, structure):
        """We check whether the items that would be created directly in
        the current context are allowed
        """
        portal_types = set(item["@type"] for item in structure["items"].values())
        allowed = [fti.getId() for fti in self.context.allowedContentTypes()]
        for portal_type in portal_types:
            if portal_type not in allowed:
                raise BadRequest("Some of the objects cannot be added here")

    def reply(self):
        files = self.extract_data()
        self.check_permission()
        structure = self.extract_structure(files)
        self.check_dossier_depth(structure)
        self.check_addable(structure)
        return json_compatible(structure)
