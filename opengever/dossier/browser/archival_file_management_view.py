from opengever.document.archival_file import ARCHIVAL_FILE_STATE_MAPPING
from opengever.document.behaviors.metadata import IDocumentMetadata
from plone import api
from Products.Five.browser import BrowserView


class ArchivalFileManagementView(BrowserView):
    """A view to list the archival status (whether the document has an archival
    file and its conversion status) of documents from a dossier.
    """

    def __call__(self):
        # disable Plone's editable border
        self.request.set('disable_border', True)
        return self.index()

    def get_documents(self):
        catalog = api.portal.get_tool('portal_catalog')

        docs = catalog.unrestrictedSearchResults(path=self.context.absolute_url_path(),
                                                 portal_type='opengever.document.document',
                                                 sort_on="path")
        for doc in docs:
            obj = doc.getObject()
            metadata = IDocumentMetadata(obj)
            doc_info = {}
            doc_info["path"] = obj.absolute_url_path()
            doc_info["url"] = obj.absolute_url()
            doc_info["filetype"] = doc.file_extension
            doc_info["has_archival_file"] = bool(metadata.archival_file)
            doc_info["archival_file_state"] = ARCHIVAL_FILE_STATE_MAPPING.get(
                metadata.archival_file_state)
            yield doc_info
