from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import WorkspaceNotFound
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from plone import api
from plone.memoize import ram
from plone.restapi.interfaces import ISerializeToJson
from time import time
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer
from plone.dexterity.utils import iterSchemata


CACHE_TIMEOUT = 24 * 60 * 60


def list_cache_key(linked_workspaces_instance, **kwargs):
    """Cache key builder for linked workspaces list.
    This cache key is per user and will get invalidated every CACHE_TIMEOUT,
    when a workspace is linked or removed from a dossier or when CACHE_TIMEOUT
    is modified.
    It also depends on additional parameters which should be btaching parameters
    of the request.
    """
    uid = linked_workspaces_instance.context.UID()
    linked_workspace_uids = '-'.join(linked_workspaces_instance.storage.list())
    userid = api.user.get_current().getId()
    timeout_key = str(time() // CACHE_TIMEOUT if CACHE_TIMEOUT > 0 else str(time()))

    cache_key = '-'.join(('linked_workspaces_storage', userid, uid,
                         linked_workspace_uids, str(CACHE_TIMEOUT), timeout_key))

    keywordarguments = '-'.join('{}={}'.format(key, value) for key, value in kwargs.items())
    if keywordarguments:
        cache_key = '{}-{}'.format(cache_key, keywordarguments)

    return cache_key


@implementer(ILinkedWorkspaces)
@adapter(IDossierMarker)
class LinkedWorkspaces(object):
    """Manages linked workspaces for an object.
    """

    def __init__(self, context):
        if context.is_subdossier():
            raise ComponentLookupError()

        self.client = WorkspaceClient()
        self.storage = LinkedWorkspacesStorage(context)
        self.context = context

    @ram.cache(lambda method, context, **kwargs: list_cache_key(context, **kwargs))
    def list(self, **kwargs):
        """Returns a JSON summary-representation of all stored workspaces.
        This function lookups all UIDs on the remote system by dispatching a
        search requests to the remote system.
        This means, unauthorized objects or not existing UIDs will be skipped
        automatically.
        """
        uids = self.storage.list()
        if not uids:
            return {'items': [], 'items_total': 0}

        return self.client.search(
            UID=uids,
            portal_type="opengever.workspace.workspace",
            metadata_fields="UID",
            **kwargs)

    def create(self, **data):
        """Creates a new workspace an links it with the current dossier.

        This function returns the serialized workspace.
        """
        workspace = self.client.create_workspace(**data)
        self.storage.add(workspace.get('UID'))
        return workspace

    def _get_linked_workspace_url(self, workspace_uid):
        if workspace_uid not in self.storage:
            raise WorkspaceNotLinked()

        workspace_url = self.client.lookup_url_by_uid(workspace_uid)

        if not workspace_url:
            raise WorkspaceNotFound()
        return workspace_url

    def copy_document_to_workspace(self, document, workspace_uid):
        """Will upload a copy of a document to a linked workspace.
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)

        file_ = document.get_file()
        document_repr = self._serialized_document_schema_fields(document)

        if not file_:
            # File only preserved in paper.
            return self.client.post(workspace_url, json=document_repr)

        portal_type = document.portal_type
        content_type = document.content_type()

        filename = document.get_filename()
        size = file_.size

        return self.client.tus_upload(workspace_url, portal_type, file_.open(),
                                      size, content_type, filename,
                                      **self._tus_document_repr(document_repr))

    def list_documents_in_linked_workspace(self, workspace_uid, **kwargs):
        """List documents contained in a linked workspace
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)

        return self.client.search(
            url_or_path=workspace_url,
            portal_type="opengever.document.document",
            metadata_fields="UID",
            **kwargs)

    def has_linked_workspaces(self):
        """Returns true if the current context has linked workspaces
        """
        return self.list().get('items_total', 0) > 0

    def _form_fields(self, obj):
        """Returns a list of all form field names of the given object.
        """
        fieldnames = []
        for schema in iterSchemata(obj):
            for fieldname in schema:
                fieldnames.append(fieldname)
        return fieldnames

    def _serialized_document_schema_fields(self, document):
        """Serializes all document schema fields.
        """
        serializer = getMultiAdapter((document, self.context.REQUEST), ISerializeToJson)
        whitelist = self._form_fields(document)
        whitelist.append('@type')
        return self._whitelisted_dict(serializer(), whitelist)

    def _tus_document_repr(self, serialized_document):
        """Prepares the serialized document to match the criterias to add a new
        document with the `tus_upload`.
        """
        return self._blacklisted_dict(serialized_document, ['@type', 'file'])

    def _whitelisted_dict(self, dict_obj, whitelist):
        whitelisted_dict = {}
        for key in whitelist:
            if key in dict_obj:
                whitelisted_dict[key] = dict_obj[key]
        return whitelisted_dict

    def _blacklisted_dict(self, dict_obj, blacklist):
        blacklisted_dict = {}
        for key in dict_obj.keys():
            if key in blacklist:
                continue
            blacklisted_dict[key] = dict_obj[key]

        return blacklisted_dict
