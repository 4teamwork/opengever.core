from ftw.upgrade import UpgradeStep
from ftw.upgrade.workflow import WorkflowChainUpdater
from opengever.dossier.interfaces import ITemplateDossierProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from plone import api


class RenameTemplateDossierToTemplateFolder(UpgradeStep):
    """Rename template dossier to template folder.
    """

    def __call__(self):
        query = {'portal_type': 'opengever.dossier.templatedossier'}
        objects = self.catalog_unrestricted_search(query, full_objects=True)
        review_state_mapping = {
            ('opengever_templatedossier_workflow', 'opengever_templatefolder_workflow'): {
                'templatedossier-state-active': 'templatefolder-state-active'}
            }

        # Save current ITemplateDossierProperties settings
        create_doc_properties = api.portal.get_registry_record(
            'create_doc_properties', ITemplateDossierProperties)

        with WorkflowChainUpdater(objects, review_state_mapping,
                                  migrate_workflow_history=False):
            self.install_upgrade_profile()

        # Restore current ITemplateDossierProperties settings
        api.portal.set_registry_record(
            'create_doc_properties',
            create_doc_properties,
            ITemplateFolderProperties)
