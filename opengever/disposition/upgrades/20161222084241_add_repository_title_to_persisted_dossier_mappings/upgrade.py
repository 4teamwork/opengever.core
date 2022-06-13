from ftw.upgrade import UpgradeStep
from opengever.base.interfaces import IReferenceNumber
from plone import api


KEY = 'repository_title'


class AddRepositoryTitleToPersistedDossierMappings(UpgradeStep):
    """Add repository title to persisted dossier mappings.
    """

    def __call__(self):
        for disposition in self.objects(
                {'portal_type': 'opengever.disposition.disposition'},
                'Add repository_title to persisted dossier_mappings'):

            self.migrate_destroyed_dossiers(disposition)
            self.migrate_history(disposition)

    def migrate_destroyed_dossiers(self, disposition):
        if not disposition.get_destroyed_dossiers():
            return

        self.migrate_mapping(disposition.get_destroyed_dossiers())

    def migrate_history(self, disposition):
        for entry in disposition.get_history():
            self.migrate_mapping(entry.mapping.get('dossiers'))

    def migrate_mapping(self, mappings):
        for item in mappings:
            if KEY not in mappings:
                item[KEY] = self.get_repository_title(
                    item.get('reference_number'))

    def get_repository_title(self, reference_number):
        formatter = IReferenceNumber(api.portal.get()).get_active_formatter()

        catalog = api.portal.get_tool('portal_catalog')
        repository_reference = reference_number.split(
            formatter.repository_dossier_seperator)
        repository = catalog(reference=repository_reference)[-1]

        # fallback for removed repositories
        if not repository:
            return u''

        return repository.Title.decode('utf-8')
