from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.behaviors.filing import IFilingNumber


class MigrateFilingNumbers(UpgradeStep):

    def __call__(self):
        for dossier in self.get_dossiers(
                {'object_provides': IDossierMarker.__identifier__},
                'Migrate filing number in to the new field'):

            self.migrate_filing_number(dossier)

    def get_dossiers(self, query, message):
        brains = self.catalog_unrestricted_search(query)
        return ProgressLogger(message, brains)

    def migrate_filing_number(self, brain):

        filing_number = brain.filing_no
        if filing_number and not filing_number.endswith('-?'):

            dossier = brain.getObject()
            IFilingNumber(dossier).filing_no = IDossier(dossier).filing_no
