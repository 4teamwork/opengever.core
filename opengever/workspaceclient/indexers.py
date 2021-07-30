from opengever.document.behaviors import IBaseDocument
from opengever.workspaceclient.interfaces import ILinkedDocuments
from plone.indexer import indexer


@indexer(IBaseDocument)
def gever_doc_uid(obj):
    linked_document = ILinkedDocuments(obj).linked_gever_document
    if linked_document:
        return linked_document.get('UID')
