from ftw.upgrade import UpgradeStep
from opengever.document.behaviors import IBaseDocument
from plone import api


class AddGeverDocUidCatalogIndex(UpgradeStep):
    """Add gever_doc_uid catalog index.
    """

    index_name = 'gever_doc_uid'

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()

        if not self.catalog_has_index(self.index_name):
            self.catalog_add_index(self.index_name, 'FieldIndex')

        catalog = api.portal.get_tool('portal_catalog')
        workspace_roots = catalog.unrestrictedSearchResults(
            portal_type='opengever.workspace.root')
        query = {
            'object_provides': IBaseDocument.__identifier__,
            'path': {'query': [root.getPath() for root in workspace_roots]},
        }

        for obj in self.objects(
                query, u'Reindex gever_doc_uid for workspace documents'):

            obj.reindexObject(idxs=[self.index_name])
