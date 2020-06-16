from datetime import date
from DateTime import DateTime
from ftw.solr.converters import to_iso8601
from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.interfaces import ISolrSettings
from ftw.upgrade import UpgradeStep
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import logging


log = logging.getLogger('ftw.upgrade')


class UpdateSolrFieldTouchedForAllDossiers(UpgradeStep):
    """Update Solr field "touched" for all dossiers.
    """

    deferrable = True

    def __call__(self):
        if not self.is_solr_enabled:
            return

        self.solr_search = getUtility(ISolrSearch)
        self.solr_connection = getUtility(ISolrConnectionManager).connection

        dossiers = self.query_dossiers()
        for index, dossier in enumerate(dossiers.docs, 1):
            self.update_touched_date(dossier)
            if index % 1000 == 0:
                log.info("Committing items {}/{} to Solr.".format(index, dossiers.num_found))
                self.solr_connection.commit()

        # Commit the remaining items to Solr.
        self.solr_connection.commit()

    @property
    def is_solr_enabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISolrSettings)
        return settings.enabled

    def query_dossiers(self):
        return self.solr_search.search(
            query=u'object_provides:"opengever.dossier.behaviors.dossier.IDossierMarker"',
            rows=self.get_nb_dossiers()
        )

    def get_nb_dossiers(self):
        return self.solr_search.search(
            query=u'object_provides:"opengever.dossier.behaviors.dossier.IDossierMarker"'
        ).num_found

    def update_touched_date(self, dossier):
        solr_response = self.solr_search.search(
            query=u'path_parent:"{0}"'.format(dossier['path']),
            sort='modified desc',
            rows=1
        )
        if not solr_response.num_found >= 1:
            return

        newest_doc = solr_response.docs[0]
        modified = DateTime(newest_doc["modified"])
        touched = date(modified.year(), modified.month(), modified.day())

        data = {"UID": dossier["UID"], "touched": {"set": to_iso8601(touched)}}
        self.solr_connection.add(data)
