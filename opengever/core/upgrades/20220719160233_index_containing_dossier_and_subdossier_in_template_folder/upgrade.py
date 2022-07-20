from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer
from plone import api


class IndexContainingDossierAndSubdossierInTemplateFolder(UpgradeStep):
    """Index containing_dossier and subdossier in template folder
    """

    deferrable = True

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        templatefolder_query = {'path': {'query': portal_path, 'depth': 1},
                                'portal_type': 'opengever.dossier.templatefolder'}
        templatefolder_paths = [brain.getPath() for brain in catalog(templatefolder_query)]

        for templatefolder_path in templatefolder_paths:
            query = {'path': {'query': templatefolder_path},
                     'portal_type': 'opengever.document.document'}

            with NightlyIndexer(idxs=["containing_dossier", "containing_subdossier"],
                                index_in_solr_only=True) as indexer:
                for brain in self.brains(query, "Index containing_dossier and containing_subdossier"):
                    indexer.add_by_brain(brain)
