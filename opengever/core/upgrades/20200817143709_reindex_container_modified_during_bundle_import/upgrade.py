from ftw.solr.browser.maintenance import solr_date
from ftw.solr.interfaces import ISolrConnectionManager
from ftw.upgrade import UpgradeStep
from plone.dexterity.interfaces import IDexterityContainer
from zope.component import queryUtility
import logging

LOG = logging.getLogger('ftw.upgrade')


class ReindexContainerModifiedDuringBundleImport(UpgradeStep):
    """Reindex container modified during bundle import.

    The problematic containers are identified by the fact that the modified
    date on the object is different from the modified date in the catalog.
    This leads to objects that have a different modified date in solr than in
    the catalog. We use this to easily identify the problematic objects and
    avoid reindexing all containers.
    """

    deferrable = True

    def __call__(self):
        self.install_upgrade_profile()
        portal_types = [
            u'opengever.dossier.businesscasedossier',
            u'opengever.repository.repositoryfolder',
            u'opengever.repository.repositoryroot',
            u'opengever.workspace.folder',
            u'opengever.workspace.root',
            u'opengever.workspace.workspace']
        items = self.catalog_unrestricted_search(
            {'portal_type': portal_types})
        catalog_modified = set(
            [(item.UID, solr_date(item.modified)) for item in items])

        manager = queryUtility(ISolrConnectionManager)
        conn = manager.connection
        resp = conn.search({
            u'query': u'portal_type:({})'.format(u' OR '.join(portal_types)),
            u'limit': 10000000,
            u'params': {u'fl': ['UID', 'modified']},
        })
        solr_modified = set(
            [(doc['UID'], doc.get('modified', u'2000-01-01T00:00:00.000Z'))
             for doc in resp.docs])

        not_in_sync = [item[0] for item in catalog_modified - solr_modified]

        for plone_uid in not_in_sync:
            # Do not duplicate this upgrade step as is. Querying the catalog
            # for each object will trigger flushing of the indexing queue,
            # i.e. the indexing queue gets processed for every object...
            brains = self.catalog_unrestricted_search({'UID': plone_uid})
            if len(brains) != 1:
                LOG.error(
                    'Could not find a unique brain for the UID={}'.format(plone_uid)
                )
                continue
            brains[0].getObject().reindexObject(idxs=['modified'])
