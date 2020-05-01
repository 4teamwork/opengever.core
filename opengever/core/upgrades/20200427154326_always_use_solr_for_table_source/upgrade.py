from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from opengever.contact.contact import IContact
from opengever.dossier.behaviors.dossier import IDossierMarker
from zope.component import getMultiAdapter
from zope.component import getUtility


class AlwaysUseSolrForTableSource(UpgradeStep):
    """Always use solr for table source.
    """

    deferrable = True

    def __call__(self):
        self.index_email2_in_solr()
        self.index_retention_expiration_in_solr()

    def index_email2_in_solr(self):
        manager = getUtility(ISolrConnectionManager)
        contacts = self.catalog_unrestricted_search({
            'object_provides': IContact.__identifier__,
        })
        for contact in ProgressLogger('Index email2 in Solr', contacts):
            if contact.email2:
                handler = getMultiAdapter((contact, manager), ISolrIndexHandler)
                handler.add(['email2'])
        manager.connection.commit(soft_commit=False, extract_after_commit=False)

    def index_retention_expiration_in_solr(self):
        manager = getUtility(ISolrConnectionManager)
        dossiers = self.catalog_unrestricted_search({
            'object_provides': IDossierMarker.__identifier__,
            'review_state': 'dossier-state-resolved',
        })
        for dossier in ProgressLogger('Index retention_expiration in Solr', dossiers):
            if dossier.retention_expiration:
                handler = getMultiAdapter((dossier, manager), ISolrIndexHandler)
                handler.add(['retention_expiration'])
        manager.connection.commit(soft_commit=False, extract_after_commit=False)
