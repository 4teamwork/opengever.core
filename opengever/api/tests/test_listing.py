from ftw.solr.connection import SolrResponse
from ftw.solr.interfaces import ISolrSearch
from ftw.testbrowser import browsing
from mock import Mock
from opengever.api.listing import filename
from opengever.api.listing import filesize
from opengever.api.listing import get_path_depth
from opengever.base.solr import OGSolrContentListingObject
from opengever.base.solr import OGSolrDocument
from opengever.testing import IntegrationTestCase
from plone.uuid.interfaces import IUUID
from unittest import skip
from zope.component import getUtility


class TestListingEndpointWithoutSolr(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_raises_an_error_if_using_the_listing_endpoint_without_solr(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(self.repository_root,
                         view='@listing',
                         headers={'Accept': 'application/json'})


class TestListingEndpointWithSolr(IntegrationTestCase):
    # XXX TODO: We need to add tests for the different listing endpoints
    # once we have testing with Solr working.
    # See # https://github.com/4teamwork/opengever.core/pull/6009 for tests
    # we had for catalog listing endpoint.

    features = ('bumblebee', 'solr')

    def setUp(self):
        super(TestListingEndpointWithSolr, self).setUp()

        # Mock Solr connection
        self.conn = Mock(name='SolrConnection')
        self.conn.search.return_value = SolrResponse()
        self.solr = getUtility(ISolrSearch)
        self._manager = self.solr._manager
        self.solr._manager = Mock(name='SolrConnectionManager')
        self.solr.manager.connection = self.conn

    def tearDown(self):
        self.solr._manager = self._manager

    def test_filesize_accessor_avoids_obj_lookup(self):
        obj = OGSolrContentListingObject(OGSolrDocument(
            {"UID": "9398dad21bcd49f8a197cd50d10ea778", "filesize": 12345}))
        obj.getObject = Mock()
        self.assertEqual(filesize(obj), 12345)
        self.assertFalse(obj.getObject.called)

    def test_filename_accessor_avoids_obj_lookup(self):
        obj = OGSolrContentListingObject(OGSolrDocument(
            {"UID": "9398dad21bcd49f8a197cd50d10ea778", "filename": "Foo.pdf"}))
        obj.getObject = Mock()
        self.assertEqual(filename(obj), "Foo.pdf")
        self.assertFalse(obj.getObject.called)

    def test_filesize_accessor_with_obj_lookup(self):
        self.login(self.regular_user)
        obj = OGSolrContentListingObject(OGSolrDocument(
            {"UID": "9398dad21bcd49f8a197cd50d10ea778"}))
        obj.getObject = Mock()
        obj.getObject.return_value = self.document
        self.assertEqual(filesize(obj), self.document.file.size)
        self.assertTrue(obj.getObject.called)

    def test_filename_accessor_with_obj_lookup(self):
        self.login(self.regular_user)
        obj = OGSolrContentListingObject(OGSolrDocument(
            {"UID": "9398dad21bcd49f8a197cd50d10ea778"}))
        obj.filename = u'Vertraegsentwurf.docx'
        self.assertEqual(filename(obj), self.document.file.filename)

    @browsing
    def test_filter_by_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record=dossier-state-active')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn('review_state:(dossier\\-state\\-active)', filters)

    @browsing
    def test_filter_by_multiple_review_states(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record:list=dossier-state-active'
                '&filters.review_state:record:list=dossier-state-inactive')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(
            'review_state:(dossier\\-state\\-active OR dossier\\-state\\-inactive)',
            filters,
        )

    @browsing
    def test_filter_by_start_date(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=start'
                '&filters.start:record=2016-01-01TO2016-01-01')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(
            'start:([2016-01-01T00:00:00.000Z TO 2016-01-01T23:59:59.000Z])',
            filters,
        )

    @browsing
    def test_filter_by_deadline(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=tasks&columns:list=title'
                '&columns:list=deadline'
                '&filters.deadline:record=2016-01-01TO2016-01-01')
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(
            'deadline:([2016-01-01T00:00:00.000Z TO 2016-01-01T23:59:59.000Z])',
            filters,
        )

    @browsing
    def test_filter_by_file_extension(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=documents&columns:list=title'
                '&columns:list=start'
                '&filters.file_extension:record:list=.docx')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(u'file_extension:(.docx)', filters)

    @browsing
    def test_filter_by_document_type(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=documents&columns:list=title'
                '&columns:list=start'
                '&filters.document_type:record:list=contract')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(u'document_type:(contract)', filters)

    @browsing
    def test_filter_by_depth(self, browser):
        self.login(self.regular_user, browser=browser)

        # Guard assertion - we expect self.dossier to be on level 5
        self.assertEqual(5, get_path_depth(self.dossier))

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=start'
                '&depth=1')
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(u'path_depth:[* TO 6]', filters)

    @browsing
    def test_facet_counts(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=documents&columns:list=title'
                '&facets:list=start')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        params = self.conn.search.call_args[0][0]["params"]
        self.assertTrue(params['facet'],
                        msg="facet=true is needed to get facet counts back")
        self.assertEqual(1, params['facet.mincount'])
        self.assertEqual(['start'], params['facet.field'])

    @skip("Just a reminder to test that facets also return translated labels")
    def test_facet_labels(self):
        pass

    @browsing
    def test_excludes_searchroot(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers'
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json'})

        context_uid = IUUID(self.dossier)
        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn(u'-UID:%s' % context_uid, filters)

    @browsing
    def test_excluding_searchroot_doesnt_trip_on_objs_without_uuid(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers'
        browser.open(self.portal, view=view,
                     headers={'Accept': 'application/json'})

        portal_uid = IUUID(self.portal, None)
        self.assertIsNone(portal_uid)
        filters = self.conn.search.call_args[0][0]['filter']
        self.assertNotIn(u'-UID:%s' % portal_uid, filters)

    @browsing
    def test_search_filter_handles_special_characters(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&search=feedb\xc3\xa4ck&columns=title'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        query = self.conn.search.call_args[0][0]["query"]
        self.assertEqual(u'(Title:feedb\xe4ck* OR SearchableText:feedb\xe4ck* '
                         u'OR metadata:feedb\xe4ck*)',
                         query)

    @browsing
    def test_sort_on_existing_field(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=title&sort_on=responsible'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        sort = self.conn.search.call_args[0][0]["sort"]
        self.assertEqual('responsible desc', sort)

    @browsing
    def test_sort_on_inexistant_field(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=title&sort_on=inexistant'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        sort = self.conn.search.call_args[0][0]["sort"]
        self.assertEqual('modified desc', sort)
