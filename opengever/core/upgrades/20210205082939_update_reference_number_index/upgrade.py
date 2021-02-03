from ftw.upgrade import UpgradeStep
from opengever.dossier.templatefolder import ITemplateFolder
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.dexterity.interfaces import IDexterityContent


class UpdateReferenceNumberIndex(UpgradeStep):
    """Update reference number index.
    """

    deferrable = True

    def __call__(self):
        self.update_reference_number_index()

    def update_reference_number_index(self):
        query = {'object_provides': ITemplateFolder.__identifier__}

        results = self.catalog_unrestricted_search(query)
        paths = [brain.getPath() for brain in results]

        query = {'object_provides': IDexterityContent.__identifier__,
                 'path': paths}
        for obj in self.objects(query, 'Update reference index for template folder'):
            obj.reindexObject(idxs=['reference'])

        # Content of repository root is not affected by the wrong value
        # indexed for the repository root itself.
        query = {'object_provides': IRepositoryRoot.__identifier__}
        for obj in self.objects(query, 'Update reference index for repository root'):
            obj.reindexObject(idxs=['reference'])
