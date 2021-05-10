from opengever.document.document import is_email_upload
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.private.dossier import IPrivateDossier
from opengever.private.folder import IPrivateFolder
from opengever.repository.interfaces import IRepositoryFolder
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceFolder
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class MaximalDepthExceeded(Exception):
    """Raised when maximal depth would be exceeded by upload.
    """


class TypeNotAddable(Exception):
    """Raised when upload would add an object from a type not
    addable on the context.
    """


class IUploadStructureAnalyser(Interface):
    """Adapter interface for upload structure checking
    """


@implementer(IUploadStructureAnalyser)
@adapter(Interface)
class DefaultUploadStructureAnalyser(object):

    mail_type = 'ftw.mail.mail'
    document_type = 'opengever.document.document'
    container_type = None

    def __init__(self, context):
        self.context = context

    def __call__(self, files):
        self.check_preconditions()
        self.structure = self.extract_structure(files)
        self.check_structure()

    def check_preconditions(self):
        self.check_permission()

    def check_structure(self):
        self.check_addable()

    def container(self, relative_path):
        return {'@type': self.container_type,
                'relative_path': relative_path,
                'is_container': True,
                'items': {}}

    def file(self, relative_path, filename):
        if is_email_upload(filename):
            return {'@type': self.mail_type,
                    'is_container': False,
                    'relative_path': relative_path}
        return {'@type': self.document_type,
                'is_container': False,
                'relative_path': relative_path}

    def check_permission(self):
        if not api.user.has_permission('Add portal content', obj=self.context):
            raise Forbidden("User is not allowed to add objects here")

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

    def check_addable(self):
        """We check whether the items that would be created directly in
        the current context are allowed
        """
        portal_types = set(item["@type"] for item in self.structure["items"].values())
        allowed = [fti.getId() for fti in self.context.allowedContentTypes()]
        for portal_type in portal_types:
            if portal_type not in allowed:
                raise TypeNotAddable("Some of the objects cannot be added here")


@adapter(IDossierMarker)
class DossierUploadStructureAnalyser(DefaultUploadStructureAnalyser):
    """Additionally checks that upload would not exceed the maximal allowed
    dossier depth.
    """
    container_type = 'opengever.dossier.businesscasedossier'

    def check_structure(self):
        self.check_dossier_depth()
        super(DossierUploadStructureAnalyser, self).check_structure()

    @property
    def current_depth(self):
        return self.context._get_dossier_depth()

    def check_dossier_depth(self):
        max_depth = api.portal.get_registry_record(
            name='maximum_dossier_depth',
            interface=IDossierContainerTypes
            )
        if self.current_depth + self.structure["max_container_depth"] > max_depth + 1:
            raise MaximalDepthExceeded("Maximum dossier depth exceeded")


@adapter(IRepositoryFolder)
class RepositoryFolderUploadStructureAnalyser(DossierUploadStructureAnalyser):

    @property
    def current_depth(self):
        return 0


@adapter(IPrivateFolder)
class PrivateFolderUploadStructureAnalyser(RepositoryFolderUploadStructureAnalyser):

    container_type = 'opengever.private.dossier'


@adapter(IPrivateDossier)
class PrivateDossierUploadStructureAnalyser(DossierUploadStructureAnalyser):

    container_type = 'opengever.private.dossier'


@adapter(IWorkspace)
class WorkspaceUploadStructureAnalyser(DefaultUploadStructureAnalyser):

    container_type = 'opengever.workspace.folder'


@adapter(IWorkspaceFolder)
class WorkspaceFolderUploadStructureAnalyser(DefaultUploadStructureAnalyser):

    container_type = 'opengever.workspace.folder'


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

    def extract_data(self):
        data = json_body(self.request)
        files = data.get("files", None)
        if not files:
            raise BadRequest("Property 'files' is required")
        for file in files:
            if not file:
                raise BadRequest("Empty filename not supported")
        return files

    def reply(self):
        files = self.extract_data()
        self.check_permission()

        upload_checker = IUploadStructureAnalyser(self.context)
        try:
            upload_checker(files)
        except (MaximalDepthExceeded, TypeNotAddable) as exc:
            raise BadRequest(exc.message)
        return json_compatible(upload_checker.structure)
