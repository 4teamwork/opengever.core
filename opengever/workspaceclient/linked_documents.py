from opengever.document.behaviors import IBaseDocument
from opengever.workspaceclient.interfaces import ILinkedDocuments
from operator import itemgetter
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import json_compatible
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer


LINKED_DOCUMENT_STORAGE_KEY = 'opengever.workspaceclient.linked_documents'


class AlreadyLinkedError(Exception):
    """Raised when attempting to overwrite existing link to GEVER document.
    """


@implementer(ILinkedDocuments)
@adapter(IBaseDocument)
class LinkedDocuments(object):
    """Manages documents linked between GEVER and teamraum.
    """

    storage_key = LINKED_DOCUMENT_STORAGE_KEY

    def __init__(self, context):
        self.document = context

    @property
    def linked_workspace_documents(self):
        link_storage = self._link_storage()
        return list(link_storage.get('workspace_documents', []))

    @property
    def linked_gever_document(self):
        link_storage = self._link_storage()
        gever_doc = link_storage.get('gever_document')
        if gever_doc:
            return dict(gever_doc)

    def link_workspace_document(self, workspace_doc_uid):
        link_storage = self._link_storage(persistent=True)
        workspace_docs = link_storage.setdefault(
            'workspace_documents', PersistentList())

        # Refuse to add duplicate links
        if workspace_doc_uid in map(itemgetter('UID'), workspace_docs):
            raise AlreadyLinkedError(
                "GEVER doc %r already contains link to workspace doc %r" % (
                    self.document, workspace_doc_uid))

        workspace_doc = PersistentMapping({'UID': workspace_doc_uid})
        workspace_docs.append(workspace_doc)

    def link_gever_document(self, gever_doc_uid):
        link_storage = self._link_storage(persistent=True)

        # Refuse to overwrite existing link
        if link_storage.get('gever_document') is not None:
            raise AlreadyLinkedError(
                "Workspace doc %r is already linked to GEVER doc %r" % (
                    self.document, gever_doc_uid))

        gever_doc = PersistentMapping({'UID': gever_doc_uid})
        link_storage['gever_document'] = gever_doc

    def serialize(self):
        data = {
            'workspace_documents': self.linked_workspace_documents,
            'gever_document': self.linked_gever_document,
        }
        return json_compatible(data)

    def _link_storage(self, persistent=False):
        annotations = IAnnotations(self.document)
        if persistent:
            return annotations.setdefault(self.storage_key, PersistentMapping())
        return dict(annotations.get(self.storage_key, {}))
