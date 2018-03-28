from ftw.upgrade import UpgradeStep
from plone import api


class FixDDUploadForTemplateFolders(UpgradeStep):
    """Fix d&d upload for template folders.
    """

    def __call__(self):
        self.reindex_object_provides()

    def reindex_object_provides(self):
        catalog = api.portal.get_tool('portal_catalog')
        query = {'portal_type': ['opengever.dossier.templatefolder']}
        message = "Reindex object_provides for template folders"

        for obj in self.objects(query, message):
            catalog.reindexObject(
                obj, idxs=['object_provides'], update_metadata=False)
