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


def list_cache_key(linked_workspaces_instance):
    """Cache key builder with the current user, a timeout and an additional
    string or list to append to the key.
    """

    uid = linked_workspaces_instance.context.UID()
    linked_workspace_uids = '-'.join(linked_workspaces_instance.storage.list())
    userid = api.user.get_current().getId()
    timeout_key = str(time() // CACHE_TIMEOUT if CACHE_TIMEOUT > 0 else str(time()))
    return '-'.join(('linked_workspaces_storage', userid, uid, linked_workspace_uids,
                    str(CACHE_TIMEOUT), timeout_key))


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

    @ram.cache(lambda method, context: list_cache_key(context))
    def list(self):
        """Returns a JSON summary-representation of all stored workspaces.
        This function lookups all UIDs on the remote system by dispatching a
        search requests to the remote system.
        This means, unauthorized objects or not existing UIDs will be skipped
        automatically.
        """
        uids = self.storage.list()
        if not uids:
            return {'items': [], 'total_items': 0}

        return self.client.search(
            UID=uids,
            portal_type="opengever.workspace.workspace",
            metadata_fields="UID")

    def create(self, **data):
        """Creates a new workspace an links it with the current dossier.

        This function returns the serialized workspace.
        """
        workspace = self.client.create_workspace(**data)
        self.storage.add(workspace.get('UID'))
        return workspace

    def copy_document_to_workspace(self, document, workspace_uid):
        """Will upload a copy of a document to a linked workspace.
        """
        if workspace_uid not in self.storage:
            raise WorkspaceNotLinked()

        workspace_url = self.client.lookup_url_by_uid(workspace_uid)

        if not workspace_url:
            raise WorkspaceNotFound()

        file_ = document.file
        document_repr = self._serialized_document_schema_fields(document)

        if not file_:
            # File only preserved in paper.
            return self.client.post(workspace_url, json=document_repr)

        # TUS upload is not yet implemented.
        raise NotImplemented

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
        document_repr = serializer()
        whitelisted = self._form_fields(document)
        whitelisted.append('@type')
        keys = document_repr.keys()
        for key in keys:
            if key not in whitelisted:
                del document_repr[key]

        return document_repr
