from collections import defaultdict
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_path_filter
from opengever.api import _
from opengever.api.not_reported_exceptions import BadRequest as NotReportedBadRequest
from opengever.api.not_reported_exceptions import Forbidden as NotReportedForbidden
from opengever.document.document import is_email_upload
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.templatefolder import get_template_folder
from opengever.dossier.templatefolder.interfaces import ITemplateFolder
from opengever.dossier.utils import get_main_dossier
from opengever.private.dossier import IPrivateDossier
from opengever.private.folder import IPrivateFolder
from opengever.repository.interfaces import IRepositoryFolder
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.utils import get_containing_workspace
from plone import api
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getUtility
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
        self.find_possible_duplicates(files)

    def check_preconditions(self):
        self.check_permission()

    def check_structure(self):
        self.check_addable()

    @property
    def duplicate_search_root(self):
        return get_main_dossier(self.context) or self.context

    def find_possible_duplicates(self, files):
        solr = getUtility(ISolrSearch)
        if not self.duplicate_search_root:
            self.structure['possible_duplicates'] = {}
            return

        path = '/'.join(self.duplicate_search_root.getPhysicalPath())
        filters = make_path_filter(path, depth=-1)

        normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')
        normalized_filenames = {}
        for file in files:
            filename = file.rsplit("/")[-1]
            normalized_filenames[file] = normalizer.normalize(filename)

        quoted_filenames = ['"{}"'.format(el) for el in normalized_filenames.values()]
        filters.append(
            u'filename:({})'.format(' OR '.join(quoted_filenames))
        )

        resp = solr.search(
            filters=filters,
            fl=['path', 'filename', 'Title', 'portal_type', ])

        serialized_docs = defaultdict(list)
        for doc in resp.docs:
            serialized_docs[doc.get('filename')].append(
                {'@id': doc.get('path'),
                 '@type': doc.get('portal_type'),
                 'title': doc.get('Title'),
                 'filename': doc.get('filename')}
            )
        possible_duplicates = {}
        for file in files:
            normalized_filename = normalized_filenames[file]
            if normalized_filename in serialized_docs:
                possible_duplicates[file] = serialized_docs[normalized_filename]
        self.structure['possible_duplicates'] = possible_duplicates

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
            raise NotReportedForbidden("User is not allowed to add objects here")

    def extract_structure(self, files):
        root = {'items': {}}
        max_depth = 0
        items_total = 0
        for path in sorted(files):
            curr_depth = 0
            segments = path.split("/")
            parent = root
            for i, segment in enumerate(segments[:-1]):
                relative_path = "/".join(segments[:i + 1])
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
                raise TypeNotAddable(
                    _('msg_some_objects_not_addable',
                      u'Some of the objects cannot be added here'))


class DossierDepthCheckMixin(object):
    """Additionally checks that upload would not exceed the maximal allowed
    dossier depth.
    """
    def check_structure(self):
        self.check_dossier_depth()
        super(DossierDepthCheckMixin, self).check_structure()

    @property
    def current_depth(self):
        return 0

    def check_dossier_depth(self):
        # It is only a file upload
        if self.structure["max_container_depth"] == 0:
            return

        if not self.context.is_dossier_structure_addable(
                self.structure["max_container_depth"]):
            raise MaximalDepthExceeded(
                _(u'msg_max_dossier_depth_exceeded',
                  default=u'Maximum dossier depth exceeded'))


@adapter(IDossierMarker)
class DossierUploadStructureAnalyser(DossierDepthCheckMixin, DefaultUploadStructureAnalyser):

    container_type = 'opengever.dossier.businesscasedossier'

    @property
    def current_depth(self):
        return self.context._get_dossier_depth()


@adapter(IRepositoryFolder)
class RepositoryFolderUploadStructureAnalyser(DossierDepthCheckMixin, DefaultUploadStructureAnalyser):

    container_type = 'opengever.dossier.businesscasedossier'

    @property
    def duplicate_search_root(self):
        return None


@adapter(IPrivateFolder)
class PrivateFolderUploadStructureAnalyser(DossierDepthCheckMixin, DefaultUploadStructureAnalyser):

    container_type = 'opengever.private.dossier'

    @property
    def duplicate_search_root(self):
        return None


@adapter(IPrivateDossier)
class PrivateDossierUploadStructureAnalyser(DossierDepthCheckMixin, DefaultUploadStructureAnalyser):

    container_type = 'opengever.private.dossier'

    @property
    def current_depth(self):
        return self.context._get_dossier_depth()


@adapter(IWorkspace)
class WorkspaceUploadStructureAnalyser(DefaultUploadStructureAnalyser):

    container_type = 'opengever.workspace.folder'

    @property
    def duplicate_search_root(self):
        return self.context


@adapter(IWorkspaceFolder)
class WorkspaceFolderUploadStructureAnalyser(DefaultUploadStructureAnalyser):

    container_type = 'opengever.workspace.folder'

    @property
    def duplicate_search_root(self):
        return get_containing_workspace(self.context)


@adapter(ITemplateFolder)
class TemplateFolderUploadStructureAnalyser(DefaultUploadStructureAnalyser):

    @property
    def duplicate_search_root(self):
        return get_template_folder()


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
            raise BadRequest(_(u'msg_prop_file_required',
                               default=u"Property 'files' is required"))
        for file in files:
            if not file:
                raise BadRequest(
                    _(u'msg_filename_required',
                      default=u"Empty filename not supported"))

        return files

    def reply(self):
        files = self.extract_data()
        self.check_permission()

        upload_checker = IUploadStructureAnalyser(self.context)
        try:
            upload_checker(files)
        except (MaximalDepthExceeded, TypeNotAddable) as exc:
            raise NotReportedBadRequest(exc.message)
        return json_compatible(upload_checker.structure)
