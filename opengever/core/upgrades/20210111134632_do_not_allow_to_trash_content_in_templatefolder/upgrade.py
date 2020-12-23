from ftw.upgrade import UpgradeStep
from opengever.trash.trash import ITrashable
from plone import api


class DoNotAllowToTrashContentInTemplatefolder(UpgradeStep):
    """Do not allow to trash content in templatefolder.
    """

    def __call__(self):
        self.untrash_trashed_documents_in_template_folder()
        self.install_upgrade_profile()
        self.update_workflow_security(['opengever_templatefolder_workflow'],
                                      reindex_security=False)

    def untrash_trashed_documents_in_template_folder(self):
        catalog = api.portal.get_tool('portal_catalog')
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        templatefolder_query = {'path': {'query': portal_path, 'depth': 1},
                                'portal_type': 'opengever.dossier.templatefolder'}
        templatefolder_paths = [brain.getPath() for brain in catalog(templatefolder_query)]
        for templatefolder_path in templatefolder_paths:
            document_query = {'path': {'query': templatefolder_path},
                              'object_provides': 'opengever.document.behaviors.IBaseDocument',
                              'trashed': True}
            for obj in self.objects(document_query, 'Untrash trashed documents in templatefolder'):
                ITrashable(obj).untrash()
