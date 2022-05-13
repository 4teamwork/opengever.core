from ftw.upgrade import UpgradeStep
from opengever.document.interfaces import ITemplateDocumentMarker
from plone import api
from zope.interface import alsoProvides


class MarkTemplateDocumentsWithInterface(UpgradeStep):
    """Mark template documents with interface.
    """

    deferrable = True

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        templatefolder_query = {'path': {'query': portal_path},
                                'portal_type': 'opengever.dossier.templatefolder'}
        templatefolder_paths = [brain.getPath() for brain in catalog(templatefolder_query)]

        for templatefolder_path in templatefolder_paths:
            document_query = {'path': {'query': templatefolder_path, 'depth': 1},
                              'object_provides': 'opengever.document.behaviors.IBaseDocument'}
            for obj in self.objects(document_query, 'Mark document templates as ITemplateDocumentMarker'):
                alsoProvides(obj, ITemplateDocumentMarker)
                obj.reindexObject(idxs=['object_provides'])
