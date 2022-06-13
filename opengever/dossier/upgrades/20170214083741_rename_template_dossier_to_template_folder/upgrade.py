from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from ftw.upgrade.workflow import WorkflowChainUpdater
from opengever.dossier.interfaces import ITemplateDossierProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.dossier.templatefolder.templatefolder import TemplateFolder
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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
                                  migrate_workflow_history=False) as updater:
            self.install_upgrade_profile()
            for obj in ProgressLogger("Migrate type opengever.dossier.templatedossier "
                                      "to opengever.dossier.templatefolder",
                                      updater.objects):

                self.migrate_class(obj, TemplateFolder)
                obj.portal_type = 'opengever.dossier.templatefolder'
                notify(ObjectModifiedEvent(obj))

        # Restore current ITemplateDossierProperties settings
        api.portal.set_registry_record(
            'create_doc_properties',
            create_doc_properties,
            ITemplateFolderProperties)
