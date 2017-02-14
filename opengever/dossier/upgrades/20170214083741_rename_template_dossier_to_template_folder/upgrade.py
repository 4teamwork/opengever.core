from ftw.upgrade import UpgradeStep
from opengever.dossier.interfaces import ITemplateDossierProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from plone import api


class RenameTemplateDossierToTemplateFolder(UpgradeStep):
    """Rename template dossier to template folder.
    """

    def __call__(self):
        # Save current ITemplateDossierProperties settings
        create_doc_properties = api.portal.get_registry_record(
            'create_doc_properties', ITemplateDossierProperties)

        self.install_upgrade_profile()

        # Restore current ITemplateDossierProperties settings
        api.portal.set_registry_record(
            'create_doc_properties',
            create_doc_properties,
            ITemplateFolderProperties)
