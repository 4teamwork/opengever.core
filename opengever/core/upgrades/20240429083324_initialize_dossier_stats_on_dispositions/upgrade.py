from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from persistent.dict import PersistentDict
from Products.CMFPlone.utils import safe_hasattr


class InitializeDossierStatsOnDispositions(UpgradeStep):
    """Initialize dossier stats on dispositions.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'opengever.disposition.disposition'}
        for obj in ProgressLogger('Initializing dossier stats',
                                  self.catalog_unrestricted_search(query, full_objects=True)):
            if not safe_hasattr(obj, 'stats_by_dossier'):
                self.initialize_stats(obj)

    def initialize_stats(self, disposition):
        disposition.stats_by_dossier = PersistentDict()
        for dossier in disposition.get_dossiers():
            if dossier:
                stats = disposition.query_stats(dossier)
                disposition.stats_by_dossier[dossier.UID()] = PersistentDict(stats)
