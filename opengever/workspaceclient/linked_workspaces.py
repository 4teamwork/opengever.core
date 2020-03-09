from opengever.api.add import GeverFolderPost
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.workspaceclient.client import WorkspaceClient
from opengever.workspaceclient.exceptions import WorkspaceNotFound
from opengever.workspaceclient.exceptions import WorkspaceNotLinked
from opengever.workspaceclient.interfaces import ILinkedWorkspaces
from opengever.workspaceclient.storage import LinkedWorkspacesStorage
from plone import api
from plone.dexterity.utils import iterSchemata
from plone.memoize import ram
from plone.restapi.interfaces import ISerializeToJson
from time import time
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.globalrequest import getRequest
from zope.interface import implementer

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


class ProxyPost(GeverFolderPost):
    """When copying a document back from Workspace into GEVER, we GET the
    document from the workspace so that we have the serialized data. We then
    need to deserialize this to create a new object in the dossier. The process
    needed for this creation is the same as in a POST request to GEVER (i.e.
    create an object in the void, get the correct deserializer and deserialize
    the data into the object, add the object to the context), except
    that we already have the data and do not need to get it from the request.
    This class allows us to reuse GeverFolderPost by simply overwriting how we
    get the serialized data.
    """
    def __init__(self, data):
        self._request_data = data

    @property
    def request_data(self):
        """We have the serialized data from a previous GET request,
        and it is not contained in the request as it would be for a
        normal POST.
        """
        return self._request_data

    def serialize_object(self):
        """The reply here is not sent back to the user, so we do not
        need to serialize the object, but rather return the object itself.
        """
        return self.obj


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

    def _get_document_by_uid(self, workspace_uid, document_uid):
        linked_documents = self.list_documents_in_linked_workspace(workspace_uid)
        for document in linked_documents["items"]:
            if document.get('UID') == document_uid:
                return document

    def copy_document_from_workspace(self, workspace_uid, document_uid):
        """Will copy a document from a linked workspace.
        """
        document = self._get_document_by_uid(workspace_uid, document_uid)
        if not document:
            raise LookupError("Document not in linked workspace")

        document_url = document.get("@id")
        document_repr = self.client.get(url_or_path=document_url)

        if document_repr.get('archival_file'):
            data = self.client.request.get(document_repr['archival_file']['download'])
            document_repr['archival_file']['data'] = data.content
        if document_repr.get('file'):
            data = self.client.request.get(document_repr['file']['download'])
            document_repr['file']['data'] = data.content
        elif document_repr.get('original_message'):
            # The deserializer will copy the file in message back to
            # original_message and transform it back to an eml and store it
            # in message. Writing the original_message directly would require
            # manager permissions.
            data = self.client.request.get(document_repr['original_message']['download'])
            document_repr['message'] = document_repr.pop('original_message')
            document_repr['message']['data'] = data.content
        elif document_repr.get('message'):
            data = self.client.request.get(document_repr['message']['download'])
            document_repr['message']['data'] = data.content

        # We should avoid setting the id ourselves, can lead to conflicts
        document_repr = self._blacklisted_dict(document_repr, ['id'])

        proxy_post = ProxyPost(document_repr)
        proxy_post.context = self.context
        proxy_post.request = getRequest()
        return proxy_post.reply()

    def list_documents_in_linked_workspace(self, workspace_uid, **kwargs):
        """List documents contained in a linked workspace
        """
        workspace_url = self._get_linked_workspace_url(workspace_uid)

        return self.client.search(
            url_or_path=workspace_url,
            portal_type=["opengever.document.document", "ftw.mail.mail"],
            metadata_fields=["UID", "filename"],
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
        return self._blacklisted_dict(
            serialized_document,
            ['@type', 'file', 'archival_file', 'message', 'original_message'])

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
