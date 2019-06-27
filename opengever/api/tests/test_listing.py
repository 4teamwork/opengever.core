from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
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
from zope.component import getUtility


class TestListingEndpoint(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_dossier_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=dossiers',
            'columns=reference',
            'columns=title',
            'columns=review_state',
            'columns=responsible_fullname',
            'columns=relative_path',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'review_state': u'dossier-state-active',
             u'responsible_fullname': u'Ziegler Robert',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
             u'reference': u'Client1 1.1 / 1',
             u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
            browser.json['items'][-1])

    @browsing
    def test_document_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=documents',
            'columns=reference',
            'columns=title',
            'columns=modified',
            'columns=document_author',
            'columns=containing_dossier',
            'columns=bumblebee_checksum',
            'columns=relative_path',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(
            {u'reference': u'Client1 1.1 / 1 / 14',
             u'title': u'Vertr\xe4gsentwurf',
             u'document_author': u'test_user_1_',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
             u'modified': u'2016-08-31T14:07:33+00:00',
             u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'bumblebee_checksum': DOCX_CHECKSUM,
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14'},
            browser.json['items'][-1])

    @browsing
    def test_document_listing_preview_url(self, browser):
        self.login(self.regular_user, browser)
        query_string = '&'.join((
            'name=documents',
            'columns:list=preview_url',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/preview',
            browser.json['items'][-1]['preview_url'][:124],
        )

    @browsing
    def test_document_listing_pdf_url(self, browser):
        self.login(self.regular_user, browser)
        query_string = '&'.join((
            'name=documents',
            'columns:list=pdf_url',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/pdf',
            browser.json['items'][-1]['pdf_url'][:120],
        )

    @browsing
    def test_file_information(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=filename&columns=filesize&sort_on=created'
        browser.open(self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertEqual(
            {u'@id': self.document.absolute_url(),
             u'filesize': self.document.file.size,
             u'filename': u'Vertraegsentwurf.docx'},
            browser.json['items'][-1])

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
    def test_batching(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        all_dossiers = browser.json['items']

        # batched no start point
        view = '@listing?name=dossiers&b_size=3'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_dossiers[0:3], browser.json['items'])

        # batched with start point
        view = '@listing?name=dossiers&b_size=2&b_start=4'
        browser.open(
            self.repository_root, view=view, headers={'Accept': 'application/json'})
        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(all_dossiers[4:6], browser.json['items'])

    @browsing
    def test_search_filter(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&search=feedback&columns=title'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})
        self.assertEqual(
            [self.taskdocument.absolute_url()],
            [item['@id'] for item in browser.json['items']])

    @browsing
    def test_current_context_is_excluded(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers&columns:list=title&sort_on=created'
        browser.open(
            self.dossier, view=view, headers={'Accept': 'application/json'})

        self.assertNotIn(
            self.dossier.Title().decode('utf8'),
            [d['title'] for d in browser.json['items']],
        )

    @browsing
    def test_review_state_and_review_state_label(self, browser):
        self.enable_languages()

        self.login(self.regular_user, browser=browser)
        view = '@listing?name=dossiers&columns=title&columns=review_state&columns=review_state_label&sort_on=created'
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        item = browser.json['items'][0]
        self.assertEqual(u'dossier-state-active', item[u'review_state'])
        self.assertEqual(u'In Bearbeitung', item[u'review_state_label'])

    @browsing
    def test_filter_by_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record=dossier-state-active')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        items = browser.json['items']
        review_states = list(set(map(lambda x: x['review_state'], items)))
        self.assertEqual(1, len(review_states))
        self.assertEqual('dossier-state-active', review_states[0])

    @browsing
    def test_filter_by_multiple_review_states(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record:list=dossier-state-active'
                '&filters.review_state:record:list=dossier-state-inactive')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        items = browser.json['items']
        review_states = list(set(map(lambda x: x['review_state'], items)))
        self.assertEqual(2, len(review_states))
        self.assertIn('dossier-state-active', review_states)
        self.assertIn('dossier-state-inactive', review_states)

    @browsing
    def test_filter_by_start_date(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=start'
                '&filters.start:record=2016-01-01TO2016-01-01')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        items = browser.json['items']
        start_dates = list(set(map(lambda x: x['start'], items)))
        self.assertEqual(1, len(start_dates))
        self.assertEqual('2016-01-01', start_dates[0])

    @browsing
    def test_filter_by_deadline(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=tasks&columns:list=title&columns:list=deadline'
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json'})

        items = browser.json['items']
        self.assertTrue(
            len(items) > 1,
            msg="There should be several tasks in the listing before filtering")

        view = '{}&filters.deadline:record=2016-08-01TO2016-10-01'.format(view)
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json'})

        items = browser.json['items']
        deadlines = list(set(map(lambda x: x['deadline'], items)))
        self.assertEqual(1, len(deadlines))
        self.assertEqual('2016-09-05', deadlines[0])

    @browsing
    def test_workspaces_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=workspaces',
            'columns=title',
            'columns=description',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace_root, view=view, headers={'Accept': 'application/json'})

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1',
             u'title': u'A Workspace',
             u'description': u'A Workspace description'},
            browser.json['items'][-1])

    @browsing
    def test_workspace_folders_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=workspace_folders',
            'columns=title',
            'columns=description',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers={'Accept': 'application/json'})

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/folder-1',
             u'title': u'WS F\xc3lder',
             u'description': u'A Workspace folder description'},
            browser.json['items'][-1])

    @browsing
    def test_tasks_listing(self, browser):
        self.enable_languages()

        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=tasks',
            'columns=review_state_label',
            'columns=title',
            'columns=task_type',
            'columns=deadline',
            'columns=completed',
            'columns=responsible_fullname',
            'columns=issuer_fullname',
            'columns=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        item = filter(lambda item: item.get('@id') == self.task.absolute_url(),
                      browser.json['items'])[0]

        self.assertItemsEqual(
            {u'issuer_fullname': u'Ziegler Robert',
             u'task_type': u'Zur Pr\xfcfung / Korrektur',
             u'responsible_fullname': u'B\xe4rfuss K\xe4thi',
             u'completed': None,
             u'created': u'2016-08-31T16:01:33+00:00',
             u'deadline': u'2016-11-01',
             u'review_state_label': u'In Arbeit',
             u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1'},
            item)

    @browsing
    def test_filter_by_file_extension(self, browser):
        self.login(self.regular_user, browser=browser)

        # all documents
        view = ('@listing?name=documents&'
                'columns:list=filename&columns:list=start')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        filenames = [item['filename'] for item in browser.json['items']]

        # docx documents only
        view = ('@listing?name=documents&'
                'columns:list=filename&columns:list=start'
                '&filters.file_extension:record:list=.docx')
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertNotEqual(len(filenames), len(browser.json['items']))
        self.assertEqual(
            [filename for filename in filenames if filename.endswith('.docx')],
            [item['filename'] for item in browser.json['items']])

    @browsing
    def test_filter_by_document_type(self, browser):
        self.login(self.regular_user, browser=browser)

        # all documents
        view = '@listing?name=documents&columns:list=title&columns:list=start'
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        number_of_documents = len(browser.json['items'])


        # filtered on document_type
        view = ('@listing?name=documents&'
                'columns:list=title&columns:list=start'
                '&filters.document_type:record:list=contract')
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertNotEqual(number_of_documents, len(browser.json['items']))
        self.assertEqual(1, len(browser.json['items']))
        item = browser.json['items'][0]
        self.assertEqual(self.document.absolute_url(), item['@id'])
        self.assertEqual(self.document.title, item['title'])

    @browsing
    def test_filter_by_depth(self, browser):
        self.login(self.regular_user, browser=browser)

        # all subdossiers
        view = '@listing?name=dossiers&columns:list=title'
        browser.open(self.dossier, view=view, headers=self.api_headers)
        number_of_subdossiers = len(browser.json['items'])

        # subdossiers limited to depth 1
        view = ('@listing?name=dossiers&'
                'columns:list=title'
                '&depth=1')
        browser.open(self.dossier, view=view, headers=self.api_headers)

        self.assertTrue(number_of_subdossiers > len(browser.json['items']))
        self.assertEqual(2, len(browser.json['items']))
        self.assertItemsEqual(
            [u'2015', u'2016'],
            [item['title'] for item in browser.json['items']])


class TestListingEndpointWithSolr(IntegrationTestCase):

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

    @browsing
    def test_filter_by_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record=dossier-state-active')
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json'})

        filters = self.conn.search.call_args[0][0]['filter']
        self.assertIn('review_state:(dossier-state-active)', filters)

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
            'review_state:(dossier-state-active OR dossier-state-inactive)',
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
