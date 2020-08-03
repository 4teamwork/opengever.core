from ftw.solr.interfaces import ISolrConnectionManager
from ftw.solr.interfaces import ISolrIndexHandler
from ftw.solr.interfaces import ISolrSearch
from opengever.testing.integration_test_case import SolrIntegrationTestCase
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility


class TestSolrMaintenanceView(SolrIntegrationTestCase):
    """As `ftw.solr` does not test against a real solr we have some basic
    somke-tests that ensure it works as expected.
    """

    def setUp(self):
        super(TestSolrMaintenanceView, self).setUp()
        self.solr_maintenance = getMultiAdapter(
            (self.portal, self.request), name=u'solr-maintenance')
        self.solr_manager = getUtility(ISolrConnectionManager)
        self.solr_search = getUtility(ISolrSearch)

    def _get_solr_index_handler(self, obj):
        return getMultiAdapter((obj, self.solr_manager), ISolrIndexHandler)

    def test_default_fixture_has_empty_diff(self):
        self.login(self.manager)

        not_in_catalog, not_in_solr, not_in_sync = self.solr_maintenance.diff()
        self.assertEqual(set(), not_in_catalog)
        self.assertEqual(set(), not_in_solr)
        self.assertEqual([], not_in_sync)

    def test_solr_diff_picks_up_docs_with_empty_created_fields(self):
        self.login(self.manager)

        document_uid = IUUID(self.document)
        solr_query = 'UID:{}'.format(document_uid)

        handler = self._get_solr_index_handler(self.document)

        # make sure doc is in solr as expected
        resp = self.solr_search.search(query=solr_query)
        self.assertEqual(1, resp.num_found)

        # remove document from solr
        connection = self.get_solr_connection()
        connection.delete(IUUID(self.document))
        self.commit_solr()

        resp = self.solr_search.search(query=solr_query)
        self.assertEqual(0, resp.num_found)

        # re-add document with an atomic update for a subset of field. this
        # will store a partial document in solr, but the created field will be
        # missing from the solr document
        data = handler.get_data(['modified', 'allowedRolesAndUsers', 'path'])
        atomic_data = handler.add_atomic_update_modifier(data, 'UID')
        connection.add(atomic_data)
        self.commit_solr()

        # test solr query detects documents with missing created field
        incomplete = connection.search({
            u'query': u'-created:[* TO *]',
            u'limit': 10000000,
            u'params': {u'fl': 'UID'},
        })
        self.assertEqual(1, incomplete.num_found)
        self.assertEqual(document_uid, incomplete.docs[0]['UID'])

        # test solr maintenance view detects documents correctly
        not_in_catalog, not_in_solr, not_in_sync = self.solr_maintenance.diff()
        self.assertEqual(set(), not_in_catalog)
        self.assertEqual(set(), not_in_solr)
        self.assertEqual([document_uid], not_in_sync)

    def test_solr_diff_picks_up_docs_not_in_solr(self):
        self.login(self.manager)

        document_uid = IUUID(self.document)
        solr_query = 'UID:{}'.format(document_uid)

        # make sure doc is in solr as expected
        resp = self.solr_search.search(query=solr_query)
        self.assertEqual(1, resp.num_found)

        # remove document from solr
        connection = self.get_solr_connection()
        connection.delete(IUUID(self.document))
        self.commit_solr()

        resp = self.solr_search.search(query=solr_query)
        self.assertEqual(0, resp.num_found)

        # test solr maintenance view detects documents correctly
        not_in_catalog, not_in_solr, not_in_sync = self.solr_maintenance.diff()
        self.assertEqual(set(), not_in_catalog)
        self.assertEqual(set([document_uid]), not_in_solr)
        self.assertEqual([document_uid], not_in_sync)
