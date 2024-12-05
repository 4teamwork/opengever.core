from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from mock import Mock
from opengever.activity import notification_center
from opengever.api.listing import ALLOWED_ORDER_GROUP_FIELDS
from opengever.api.listing import ListingGet
from opengever.base.solr import OGSolrContentListingObject
from opengever.base.solr import OGSolrDocument
from opengever.base.solr.fields import filename
from opengever.base.solr.fields import filesize
from opengever.base.solr.fields import filter_escape
from opengever.document.approvals import APPROVED_IN_CURRENT_VERSION
from opengever.document.approvals import IApprovalList
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from opengever.dossier.behaviors.dossier import CHECKLIST_CLOSED_STATE
from opengever.dossier.behaviors.dossier import CHECKLIST_OPEN_STATE
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.integration_test_case import SolrIntegrationTestCase
from plone.uuid.interfaces import IUUID
from unittest import skip
from zope.component import getMultiAdapter
import requests_mock


class TestListingEndpointWithoutSolr(IntegrationTestCase):

    features = ('bumblebee',)

    @browsing
    def test_raises_an_error_if_using_the_listing_endpoint_without_solr(self, browser):
        self.deactivate_feature('solr')
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(code=400):
            browser.open(self.repository_root,
                         view='@listing',
                         headers=self.api_headers)

    def test_filter_escape(self):
        self.assertEqual('" leading whitespace\\!"', filter_escape(' leading whitespace!'))
        self.assertEqual('"trailing whitespace\\? "', filter_escape('trailing whitespace? '))
        self.assertEqual('no_whitespace', filter_escape('no_whitespace'))
        self.assertEqual('no_whitespace\\!', filter_escape('no_whitespace!'))
        self.assertEqual('"text with spaces"', filter_escape('text with spaces'))
        self.assertEqual('"text \\&& spaces"', filter_escape('text && spaces'))


class TestListingEndpointWithSolr(IntegrationTestCase):

    features = ('bumblebee', 'solr')

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
    def test_facet_counts(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = ('@listing?name=documents&columns:list=title'
                    '&facets:list=start')
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            params = solr.search.call_args[1]

        self.assertTrue(params['facet'],
                        msg="facet=true is needed to get facet counts back")
        self.assertEqual(1, params['facet.mincount'])
        self.assertEqual(['start'], params['facet.field'])

    @browsing
    def test_does_not_limit_facets(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = ('@listing?name=documents&columns:list=title'
                    '&facets:list=creator')
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            params = solr.search.call_args[1]

        self.assertEqual(-1, params['facet.limit'],
                        msg="Facets must not be limited")

    @browsing
    def test_excludes_searchroot(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=dossiers'
            browser.open(self.dossier, view=view,
                         headers=self.api_headers)

            context_uid = IUUID(self.dossier)
            filters = solr.search.call_args[1]['filters']

        self.assertIn(u'-UID:%s' % context_uid, filters)

    @browsing
    def test_excluding_searchroot_doesnt_trip_on_objs_without_uuid(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=dossiers'
            browser.open(self.portal, view=view,
                         headers=self.api_headers)

            portal_uid = IUUID(self.portal, None)
            self.assertIsNone(portal_uid)
            filters = solr.search.call_args[1]['filters']

        self.assertNotIn(u'-UID:%s' % portal_uid, filters)

    @browsing
    def test_search_filter_handles_special_characters(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=documents&search=feedb\xc3\xa4ck&columns=title'
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            query = solr.search.call_args[1]["query"]

        self.assertEqual('feedb\xc3\xa4ck*', query)

    @browsing
    def test_sort_on_existing_field(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=documents&columns=title&sort_on=responsible'
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            sort = solr.search.call_args[1]["sort"]

        self.assertEqual('responsible desc', sort)

    @browsing
    def test_sort_on_inexistant_field(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=documents&columns=title&sort_on=inexistant'
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            sort = solr.search.call_args[1]["sort"]

        self.assertEqual('modified desc', sort)

    @browsing
    def test_sort_on_reference_number_uses_sortable_reference_index(self, browser):
        self.login(self.regular_user, browser=browser)

        with self.mock_solr('solr_search.json') as solr:
            view = '@listing?name=documents&columns=title&sort_on=reference_number'
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)
            sort = solr.search.call_args[1]["sort"]

        self.assertEqual('sortable_reference desc', sort)


class TestListingWithRealSolr(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    maxDiff = None

    @browsing
    def test_repository_folders_translatable_title(self, browser):
        self.enable_languages()

        self.login(self.regular_user, browser=browser)
        view = '@listing?name=repository_folders&columns:list=title'
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        self.assertEqual(browser.json[u'items_total'], 4)
        self.assertEqual(u'1.1. Vertr\xe4ge und Vereinbarungen',
                         browser.json['items'][0]['title'])

        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'fr-ch'})
        self.assertEqual(u'1.1. Contrats et accords',
                         browser.json['items'][0]['title'])

    @browsing
    def test_dossier_listing_works_for_responsible_fullname(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=dossiers',
            'columns=reference',
            'columns=title',
            'columns=review_state',
            'columns=responsible_fullname',
            'columns=relative_path',
            'columns=UID',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers=self.api_headers)

    @browsing
    def test_dossier_listing(self, browser):
        self.enable_languages()
        self.login(self.regular_user, browser=browser)

        IDossier(self.dossier).dossier_type = "businesscase"
        self.dossier.reindexObject()
        self.commit_solr()

        query_string = '&'.join((
            'name=dossiers',
            'columns=blocked_local_roles',
            'columns=external_reference',
            'columns=public_trial',
            'columns=reference',
            'columns=title',
            'columns=retention_expiration',
            'columns=dossier_type_label',
            'columns=review_state',
            'columns=relative_path',
            'columns=UID',
            'columns=trashed',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view,
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})
        results = browser.json

        self.assertItemsEqual(
            [u'b_size', u'b_start', u'@id', u'items_total', u'items', u'facets'],
            results.keys())
        self.assertEqual(0, results["b_start"])
        self.assertEqual(25, results["b_size"])
        expected_url = "{}/{}".format(self.repository_root.absolute_url(),
                                      view.rsplit("&sort")[0])
        self.assertEqual(expected_url, results["@id"])
        self.assertEqual(17, results["items_total"])
        self.assertEqual(
            {u'review_state': u'dossier-state-active',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
             u'UID': IUUID(self.dossier),
             u'blocked_local_roles': False,
             u'dossier_type_label':u'Gesch\xe4ftsfall',
             u'external_reference': u'qpr-900-9001-\xf7',
             u'public_trial': u'Nicht gepr\xfcft',
             u'trashed': False,
             u'reference': u'Client1 1.1 / 1',
             u'retention_expiration': None,
             u'title': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'},
            results['items'][-1])

    @browsing
    def test_dossier_listing_sorted_on_reference_number(self, browser):
        self.enable_languages()
        self.login(self.regular_user, browser=browser)

        query_string = '&'.join((
            'name=dossiers',
            'columns=title',
            'columns=reference_number',
            'sort_on=reference_number',
            'sort_order=ascending'
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        results = browser.json

        self.assertEqual(
            [u'Client1 1.1 / 1',
             u'Client1 1.1 / 1.1',
             u'Client1 1.1 / 1.1.1',
             u'Client1 1.1 / 1.2',
             u'Client1 1.1 / 2',
             u'Client1 1.1 / 3',
             u'Client1 1.1 / 4',
             u'Client1 1.1 / 5',
             u'Client1 1.1 / 5.1',
             u'Client1 1.1 / 6',
             u'Client1 1.1 / 7',
             u'Client1 1.1 / 8',
             u'Client1 1.1 / 9',
             u'Client1 1.1 / 11',
             u'Client1 1.1 / 12',
             u'Client1 1.1 / 13',
             u'Client1 1.1 / 14'],
            [each['reference_number'] for each in results['items']]
            )

        query_string = '&'.join((
            'name=dossiers',
            'columns=title',
            'columns=reference',
            'sort_on=reference',
            'sort_order=descending'
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        results = browser.json

        self.assertEqual(
            [u'Client1 1.1 / 14',
             u'Client1 1.1 / 13',
             u'Client1 1.1 / 12',
             u'Client1 1.1 / 11',
             u'Client1 1.1 / 9',
             u'Client1 1.1 / 8',
             u'Client1 1.1 / 7',
             u'Client1 1.1 / 6',
             u'Client1 1.1 / 5.1',
             u'Client1 1.1 / 5',
             u'Client1 1.1 / 4',
             u'Client1 1.1 / 3',
             u'Client1 1.1 / 2',
             u'Client1 1.1 / 1.2',
             u'Client1 1.1 / 1.1.1',
             u'Client1 1.1 / 1.1',
             u'Client1 1.1 / 1'],
            [each['reference'] for each in results['items']]
            )

    @browsing
    def test_public_trial_facets_are_translated(self, browser):
        self.enable_languages()
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root, view='@listing?name=dossiers&facets:list=public_trial',
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        self.assertDictEqual(
            {u'public_trial': {u'unchecked': {u'count': 16, u'label': u'Nicht gepr\xfcft'},
                               u'private': {u'count': 1, u'label': u'Nicht \xf6ffentlich'}}},
            browser.json['facets'])

    @browsing
    def test_document_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=documents',
            'columns=external_reference',
            'columns=reference',
            'columns=title',
            'columns=modified',
            'columns=document_author',
            'columns=document_type_label',
            'columns=containing_dossier',
            'columns=bumblebee_checksum',
            'columns=relative_path',
            'columns=UID',
            'columns=trashed',
            'columns=approval_state',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view,
                     headers={'Accept': 'application/json', 'Accept-Language': 'de-ch'})

        self.assertEqual(
            {u'reference': u'Client1 1.1 / 1 / 14',
             u'title': u'Vertr\xe4gsentwurf',
             u'document_author': u'test_user_1_',
             u'document_type_label': u'Vertrag',
             u'external_reference': None,
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
             u'UID': IUUID(self.document),
             u'trashed': False,
             u'modified': u'2016-08-31T14:07:33+00:00',
             u'containing_dossier': u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'approval_state': None,
             u'bumblebee_checksum': DOCX_CHECKSUM,
             u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14'},
            browser.json['items'][-1])

    @skip('Reference prefix for private folders should be based on username')
    @browsing
    def test_mail_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=documents',
            'columns=reference',
            'columns=title',
            'columns=modified',
            'columns=containing_dossier',
            'columns=UID',
            'columns=trashed',
            'columns=approval_state',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.private_dossier, view=view, headers=self.api_headers)
        self.assertEqual(
            {u'reference': u'P Client1 kathi-barfuss / 1 / 37',
             u'title': u'[No Subject]',
             u'@id': u'http://nohost/plone/private/%s/dossier-14/document-37' % self.regular_user.id,
             u'UID': IUUID(self.private_mail),
             u'trashed': False,
             u'modified': u'2016-08-31T17:11:33+00:00',
             u'approval_state': None,
             u'containing_dossier': u'Mein Dossier 1'},
            browser.json['items'][0])

    @browsing
    def test_document_listing_preview_url(self, browser):
        self.login(self.regular_user, browser)
        query_string = '&'.join((
            'name=documents',
            'columns:list=preview_url',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers=self.api_headers)

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
        browser.open(self.dossier, view=view, headers=self.api_headers)
        self.assertEqual(
            'http://bumblebee/YnVtYmxlYmVl/api/v3/resource/local'
            '/51d6317494eccc4a73154625a6820cb6b50dc1455eb4cf26399299d4f9ce77b2/pdf',
            browser.json['items'][-1]['pdf_url'][:120],
        )

    @browsing
    def test_document_listing_approval_state(self, browser):
        self.login(self.regular_user, browser=browser)

        approvals = IApprovalList(self.document)
        versioner = Versioner(self.document)
        approvals.add(
            versioner.get_current_version_id(missing_as_zero=True),
            self.subtask, self.regular_user.id, datetime(2021, 7, 2))
        self.commit_solr()

        query_string = '&'.join((
            'name=documents',
            'columns:list=approval_state',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers=self.api_headers)
        self.assertEqual(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
             u'UID': IUUID(self.document),
             u'approval_state': APPROVED_IN_CURRENT_VERSION},
            browser.json['items'][-1])

    @browsing
    def test_listing_custom_properties(self, browser):
        self.login(self.regular_user, browser)

        self.subsubdocument.document_type = u'regulations'
        IDocumentCustomProperties(self.subsubdocument).custom_properties = {
            "IDocumentMetadata.document_type.regulations": {
                "yesorno": False,
                "choose": u"two",
                "num": 122333,
                "text": u"K\xe4fer\nJ\xe4ger",
                "textline": u"Kr\xe4he",
            },
        }
        self.subsubdocument.reindexObject()
        self.commit_solr()

        query_string = '&'.join((
            'name=documents',
            'columns:list=yesorno_custom_field_boolean',
            'columns:list=num_custom_field_int',
            'columns:list=choose_custom_field_string',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.subsubdossier, view=view, headers=self.api_headers)

        self.assertEqual(
            {
                u'choose_custom_field_string': u"two",
                u'num_custom_field_int': 122333,
                u'@id': self.subsubdocument.absolute_url(),
                u'UID': IUUID(self.subsubdocument),
                u'yesorno_custom_field_boolean': False
            },
            browser.json['items'][-1]
        )

    @browsing
    def test_file_information(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&columns=filename&columns=filesize&sort_on=created'
        browser.open(self.dossier, view=view, headers=self.api_headers)

        self.assertEqual(
            {u'@id': self.document.absolute_url(),
             u'UID': IUUID(self.document),
             u'filesize': self.document.file.size,
             u'filename': u'Vertraegsentwurf.docx'},
            browser.json['items'][-1])

    @browsing
    def test_batching(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        all_dossiers = browser.json['items']

        # batched no start point
        view = '@listing?name=dossiers&b_size=3'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_dossiers[0:3], browser.json['items'])

        # batched with start point
        view = '@listing?name=dossiers&b_size=2&b_start=4'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(2, len(browser.json['items']))
        self.assertEqual(all_dossiers[4:6], browser.json['items'])

    @browsing
    def test_search_filter(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=documents&search=feedb\xc3\xa4ck&columns=title'
        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)
        self.assertEqual(
            [self.taskdocument.absolute_url()],
            [item['@id'] for item in browser.json['items']])

    @browsing
    def test_document_facet_labels_are_transformed_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=documents&columns:list=title'
                '&facets:list=creator&facets:list=document_type')

        browser.open(self.repository_root, view=view, method='GET',
                     headers=self.api_headers)

        self.assertIn(u'facets', browser.json)
        facets = browser.json['facets']
        self.assertItemsEqual([u'creator', 'document_type'], facets.keys())
        self.assertItemsEqual(
            {self.committee_responsible.id: {u'count': 4, u'label': u'M\xfcller Fr\xe4nzi'},
             self.dossier_responsible.id: {u'count': 15, u'label': u'Ziegler Robert'}},
            facets[u'creator'])
        self.assertItemsEqual(
            {u'contract': {u'count': 1, u'label': u'Contract'}},
            facets[u'document_type'])

    @browsing
    def test_dossier_facet_labels_are_transformed_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        IDossier(self.dossier).dossier_type = "businesscase"
        self.dossier.reindexObject()
        self.commit_solr()

        view = ('@listing?name=dossiers&columns:list=title'
                '&facets:list=dossier_type')

        browser.open(self.repository_root, view=view, method='GET',
                     headers=self.api_headers)

        self.assertIn(u'facets', browser.json)
        facets = browser.json['facets']
        self.assertItemsEqual([u'dossier_type'], facets.keys())
        self.assertItemsEqual(
            {u'businesscase': {u'count': 1, u'label': u'Business case'}},
            facets[u'dossier_type'])

    @browsing
    def test_current_context_is_excluded(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=dossiers&columns:list=title&sort_on=created'
        browser.open(
            self.dossier, view=view, headers=self.api_headers)

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
                     headers=self.api_headers)

        items = browser.json['items']
        review_states = list(set(map(lambda x: x['review_state'], items)))
        self.assertEqual(1, len(review_states))
        self.assertEqual('dossier-state-active', review_states[0])

    @browsing
    def test_filter_by_dossier_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=documents&columns:list=title'
                '&filters.dossier_review_state:record=dossier-state-inactive')

        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)

        items = browser.json['items']
        self.assertItemsEqual([self.inactive_document.UID()],
                              [item.get('UID') for item in items])

    @browsing
    def test_filter_by_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=is_subdossier'
                '&filters.review_state:record:boolean=true')
        browser.open(self.portal, view=view,
                     headers=self.api_headers)

        items = browser.json['items']
        is_subdossier = list(set(map(lambda x: x['is_subdossier'], items)))
        self.assertEqual(1, len(is_subdossier))
        self.assertTrue(is_subdossier[0])

    @browsing
    def test_filter_by_empty_string(self, browser):
        self.login(self.regular_user, browser=browser)
        manager = getMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
        manager.checkout()
        self.document.reindexObject()
        self.commit_solr()
        view = ('@listing?name=documents&facets:list=checked_out')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(21, browser.json['items_total'])
        self.assertEqual(20, browser.json['facets']['checked_out']['']['count'])

        view = ('@listing?name=documents&facets:list=checked_out'
                '&filters.checked_out:record=')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(20, browser.json['items_total'])
        self.assertEqual(20, browser.json['facets']['checked_out']['']['count'])

    @browsing
    def test_negate_filter_query(self, browser):
        self.login(self.regular_user, browser=browser)
        view = ('@listing?name=dossiers')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(17, browser.json['items_total'])

        view = ('@listing?name=dossiers&facets:list=review_state'
                '&filters.review_state:record:list=dossier-state-active')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(12, browser.json['items_total'])

        view = ('@listing?name=dossiers&facets:list=review_state'
                '&filters.-review_state:record:list=dossier-state-active')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(5, browser.json['items_total'])

    @browsing
    def test_filter_by_keywords(self, browser):
        self.login(self.regular_user, browser=browser)
        view = ('@listing?name=documents')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(21, browser.json['items_total'])

        view = ('@listing?name=documents&filters.keywords:record:list=Wichtig')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(2, browser.json['items_total'])

        view = ('@listing?name=documents&filters.-keywords:record:list=Wichtig')
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(19, browser.json['items_total'])

    @browsing
    def test_filter_by_keywords_with_whitespace(self, browser):
        self.login(self.regular_user, browser=browser)
        url = (u'{}/@listing?name=dossiers&filters.keywords:record:list=Hello%20World'.format(
            self.repository_root.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(0, browser.json["items_total"])

        IDossier(self.dossier).keywords = (u'Hello World')
        self.dossier.reindexObject(idxs=['Subject'])
        self.commit_solr()

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, browser.json["items_total"])

    @browsing
    def test_filter_by_multiple_review_states(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=review_state'
                '&filters.review_state:record:list=dossier-state-active'
                '&filters.review_state:record:list=dossier-state-inactive')
        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)

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
                     headers=self.api_headers)

        items = browser.json['items']
        start_dates = list(set(map(lambda x: x['start'], items)))
        self.assertEqual(1, len(start_dates))
        self.assertEqual('2016-01-01T00:00:00Z', start_dates[0])

    @browsing
    def test_filter_by_date_custom_fields_for_dossier(self, browser):
        self.login(self.regular_user, browser=browser)
        IDossier(self.dossier).dossier_type = u"businesscase"
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDossier.dossier_type.businesscase")
            .with_field("date", u"birthday", u"Birthday", u"", False)
        )
        IDossierCustomProperties(self.dossier).custom_properties = {
            "IDossier.dossier_type.businesscase": {
                "birthday": date(2010, 12, 12),
            }
        }
        self.dossier.reindexObject()
        self.commit_solr()
        expected_data = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
            u'UID': u'createtreatydossiers000000000001',
            u'birthday_custom_field_date': u'2010-12-12T00:00:00Z'
        }
        view = (
            '@listing?name=dossiers'
            '&columns:list=birthday_custom_field_date'
            '&filters.birthday_custom_field_date:record=2010-12-12TO2010-12-12'
        )

        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertSequenceEqual(browser.json['items'][0], expected_data)

    @browsing
    def test_filter_by_date_custom_fields_for_document(self, browser):
        self.login(self.regular_user, browser=browser)
        IDocumentMetadata(self.document).document_type = u"offer"
        create(
            Builder("property_sheet_schema")
            .named("schema1")
            .assigned_to_slots(u"IDocumentMetadata.document_type.offer")
            .with_field("date", u"birthday", u"Birthday", u"", False)
        )
        IDocumentCustomProperties(self.document).custom_properties = {
            "IDocumentMetadata.document_type.offer": {
                "birthday": date(2010, 12, 12),
            }
        }
        self.document.reindexObject()
        self.commit_solr()
        view = (
            '@listing?name=documents'
            '&columns:list=birthday_custom_field_date'
            '&filters.birthday_custom_field_date:record=2010-12-12TO2010-12-12'
        )

        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)

        expected_data = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            u'UID': u'createtreatydossiers000000000002',
            u'birthday_custom_field_date': u'2010-12-12T00:00:00Z'
        }
        self.assertEqual(1, browser.json['items_total'])
        self.assertSequenceEqual(browser.json['items'][0], expected_data)

    @browsing
    def test_filter_by_retention_expiration(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=retention_expiration'
                '&filters.retention_expiration:record=*TO2016-05-01')
        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)

        self.assertEqual(4, browser.json['items_total'])
        items = browser.json['items']
        retention_expirations = list(set(map(lambda x: x['retention_expiration'], items)))
        self.assertEqual(2, len(retention_expirations))
        self.assertEqual([u'2013-01-01T00:00:00Z', u'2016-01-01T00:00:00Z'], retention_expirations)

    @browsing
    def test_wildcard_is_supported_by_date_filters(self, browser):
        self.login(self.regular_user, browser=browser)
        IDossier(self.subdossier).start = date(2016, 1, 1)
        IDossier(self.subsubdossier).start = date(2016, 2, 1)
        IDossier(self.subdossier2).start = date(2016, 3, 1)
        self.subdossier.reindexObject()
        self.subsubdossier.reindexObject()
        self.subdossier2.reindexObject()
        self.commit_solr()

        base_query = '@listing?name=dossiers&columns:list=start'
        browser.open(self.dossier, view=base_query, headers=self.api_headers)
        self.assertEqual(3, browser.json['items_total'])

        filtered_query = base_query + '&filters.start:record={}'

        browser.open(self.dossier, view=filtered_query.format('2016-01-02TO*'),
                     headers=self.api_headers)
        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            map(IUUID, [self.subsubdossier, self.subdossier2]),
            map(lambda item: item['UID'], browser.json['items']))

        browser.open(self.dossier, view=filtered_query.format('*TO2016-02-02'),
                     headers=self.api_headers)
        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            map(IUUID, [self.subdossier, self.subsubdossier]),
            map(lambda item: item['UID'], browser.json['items']))

        browser.open(self.dossier, view=filtered_query.format('*TO*'),
                     headers=self.api_headers)
        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            map(IUUID, [self.subdossier, self.subsubdossier, self.subdossier2]),
            map(lambda item: item['UID'], browser.json['items']))

    @browsing
    def test_date_filters_raise_bad_request_if_no_range_is_provided(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=start'
                '&filters.start:record=2016-01-01')
        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': u'Only date ranges are supported: 2016-01-01',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_date_filters_raise_bad_request_for_invalid_dates(self, browser):
        self.login(self.regular_user, browser=browser)

        view = ('@listing?name=dossiers&columns:list=title'
                '&columns:list=start'
                '&filters.start:record=nowTO2016-01-01')
        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.repository_root, view=view,
                         headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': u'Could not parse date: now',
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_filter_by_deadline(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@listing?name=tasks&columns:list=title&columns:list=deadline'
        browser.open(self.dossier, view=view,
                     headers=self.api_headers)

        items = browser.json['items']
        self.assertTrue(
            len(items) > 1,
            msg="There should be several tasks in the listing before filtering")

        view = '{}&filters.deadline:record=2016-08-01TO2016-10-01'.format(view)
        browser.open(self.dossier, view=view,
                     headers=self.api_headers)

        items = browser.json['items']
        deadlines = list(set(map(lambda x: x['deadline'], items)))
        self.assertEqual(1, len(deadlines))
        self.assertEqual('2016-09-07T00:00:00Z', deadlines[0])

    @browsing
    def test_filter_supports_unicode(self, browser):
        self.login(self.regular_user, browser=browser)

        view = (u'@listing?name=dossiers&columns:list=title'
                u'&filters.title:record=Vertr\xe4ge')
        browser.open(self.repository_root, view=view,
                     headers=self.api_headers)

        items = browser.json['items']
        titles = map(lambda x: x['title'], items)
        self.assertEqual(3, len(titles))
        self.assertItemsEqual(
            [u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
             u'Inaktive Vertr\xe4ge',
             u'Abgeschlossene Vertr\xe4ge'],
            titles)

    @browsing
    def test_workspaces_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=workspaces',
            'columns=title',
            'columns=description',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace_root, view=view, headers=self.api_headers)

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1',
             u'UID': IUUID(self.workspace),
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
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertDictEqual(
            {u'@id': u'http://nohost/plone/workspaces/workspace-1/folder-1',
             u'UID': IUUID(self.workspace_folder),
             u'title': u'WS F\xc3lder',
             u'description': u'A Workspace folder description'},
            browser.json['items'][-1])

    @browsing
    def test_workspace_meetings_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=workspace_meetings',
            'columns=title',
            'columns=responsible',
            'columns=start',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)
        self.assertEqual(1, browser.json['items_total'])
        self.assertDictEqual(
            {u'@id': self.workspace_meeting.absolute_url(),
             u'UID': IUUID(self.workspace_meeting),
             u'responsible': self.workspace_member.getId(),
             u'start': u'2016-12-08T00:00:00Z',
             u'title': u'Besprechung Kl\xe4ranlage'},
            browser.json['items'][0])

    @browsing
    def test_tasks_listing(self, browser):
        self.enable_languages()

        self.login(self.workspace_member, browser=browser)
        notification_center().add_watcher_to_resource(
            self.task, self.workspace_member.getId())
        self.commit_solr()

        query_string = '&'.join((
            'name=tasks',
            'columns=review_state_label',
            'columns=title',
            'columns=task_type',
            'columns=deadline',
            'columns=is_completed',
            'columns=responsible_fullname',
            'columns=issuer_fullname',
            'columns=UID',
            'columns=created',
            'columns=is_subtask',
            'columns=watchers',
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
             u'is_completed': False,
             u'created': u'2016-08-31T16:01:33+00:00',
             u'deadline': u'2016-11-01',
             u'review_state_label': u'In Arbeit',
             u'title': u'Vertragsentwurf \xdcberpr\xfcfen',
             u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-1',
             u'UID': IUUID(self.task),
             u'is_subtask': False,
             u'watchers': [self.workspace_member.getId()],
             },

            item)

    @browsing
    def test_proposals_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=proposals',
            'columns=UID',
            'columns=title',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.dossier, view=view, headers=self.api_headers)

        self.assertEqual(4, browser.json['items_total'])
        self.assertEqual(
            [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-4',
                    u'UID': u'createrisproposals00000000000001',
                    u'title': u'RIS-Proposal'
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-3',
                    u'UID': u'createtreatydossiers000000000011',
                    u'title': u'Initialvertrag f\xfcr Bearbeitung'
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-2',
                    u'UID': u'createtreatydossiers000000000009',
                    u'title': u'Antrag f\xfcr Kreiselbau'
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-1',
                    u'UID': u'createtreatydossiers000000000003',
                    u'title': u'Vertr\xe4ge'
                }
            ],
            browser.json['items'])

    @browsing
    def test_task_type_facets_are_translated(self, browser):
        self.enable_languages()

        self.login(self.workspace_member, browser=browser)
        browser.open(self.dossier, view='@listing?name=tasks&facets:list=task_type',
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        self.assertDictEqual(
            {u'task_type':
             {
                 u'information': {u'count': 1, u'label': u'Zur Kenntnisnahme'},
                 u'correction': {u'count': 2, u'label': u'Zur Pr\xfcfung / Korrektur'},
                 u'direct-execution': {u'count': 6, u'label': u'Zur direkten Erledigung'}
             }
             },
            browser.json['facets']
        )

    @browsing
    def test_filter_by_is_subtask(self, browser):
        self.login(self.regular_user, browser=browser)

        # all documents
        view = ('@listing?name=tasks&'
                'columns:list=title&columns:list=is_subtask')
        browser.open(self.dossier, view=view, headers=self.api_headers)
        all_tasks = browser.json['items']

        # only subtasks
        view = view + '&filters.is_subtask:record:list=true'
        browser.open(self.dossier, view=view, headers=self.api_headers)
        subtasks = browser.json['items']

        self.assertTrue(len(all_tasks) > len(subtasks) > 0)
        # Make sure that filtering by is_subtask filtered according to
        # the is_subtask field
        self.assertItemsEqual(
            [item for item in all_tasks if item.get("is_subtask")], subtasks)

        # Make sure that is_subtask is True for the expected objects.
        expected_subtasks = (self.subtask, self.seq_subtask_1,
                             self.seq_subtask_2, self.seq_subtask_3)
        self.assertItemsEqual(
            [subtask.absolute_url() for subtask in expected_subtasks],
            [item.get("@id") for item in subtasks])

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
    def test_filter_by_dossier_type(self, browser):
        self.login(self.regular_user, browser=browser)

        IDossier(self.dossier).dossier_type = "businesscase"
        self.dossier.reindexObject()
        self.commit_solr()

        # filtered on dossier_type
        view = ('@listing?name=dossiers&columns:list=title'
                '&filters.dossier_type:record:list=businesscase')
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        item = browser.json['items'][0]
        self.assertEqual(self.dossier.absolute_url(), item['@id'])
        self.assertEqual(self.dossier.title, item['title'])

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

        # depth 0 does not return anything as the context itself is excluded
        view = ('@listing?name=dossiers&'
                'columns:list=title'
                '&depth=0')
        browser.open(self.dossier, view=view, headers=self.api_headers)
        self.assertEqual(0, browser.json['items_total'])
        self.assertEqual(0, len(browser.json['items']))

    @browsing
    def test_filter_by_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        # all dossiers
        view = '@listing?name=dossiers&columns:list=is_subdossier'
        browser.open(self.leaf_repofolder, view=view, headers=self.api_headers)
        all_dossiers = browser.json['items']

        # only subdossiers
        view = view + '&filters.is_subdossier:record:list=true'
        browser.open(self.leaf_repofolder, view=view, headers=self.api_headers)
        subdossiers = browser.json['items']

        self.assertTrue(len(all_dossiers) > len(subdossiers) > 0)
        # Make sure that filtering by is_subdossier filtered according to
        # the is_subdossier field
        self.assertItemsEqual(
            [item for item in all_dossiers if item.get("is_subdossier")],
            subdossiers)

        # Make sure that is_subdossier is True for the expected objects.
        expected_subdossiers = (self.subdossier, self.subsubdossier,
                                self.subdossier2, self.resolvable_subdossier)
        self.assertItemsEqual(
            [subdossier.absolute_url() for subdossier in expected_subdossiers],
            [item.get("@id") for item in subdossiers])

    @browsing
    def test_filter_by_issuer(self, browser):
        self.login(self.regular_user, browser=browser)

        # all tasks
        view = '@listing?name=tasks&columns:list=issuer'
        browser.open(self.dossier, view=view, headers=self.api_headers)
        all_tasks = browser.json['items']

        # only task issued by specific user
        view = view + '&filters.issuer:record:list={}'.format(self.regular_user.getId(),)
        browser.open(self.leaf_repofolder, view=view, headers=self.api_headers)
        filtered_tasks = browser.json['items']

        self.assertTrue(len(all_tasks) > len(filtered_tasks) > 0)
        # Make sure that filtering by issuer filtered according to
        # the issuer field
        self.assertItemsEqual(
            [item for item in all_tasks if item.get("issuer") == self.regular_user.getId()],
            filtered_tasks)

        # Make sure that issuer is the right user for the expected objects.
        expected_tasks = (self.sequential_task, )
        self.assertItemsEqual(
            [task.absolute_url() for task in expected_tasks],
            [item.get("@id") for item in filtered_tasks])

    @browsing
    def test_filter_by_author_with_whitespace(self, browser):
        self.login(self.regular_user, browser=browser)

        IDocumentMetadata(self.subdocument).document_author = "Some User"
        IDocumentMetadata(self.subsubdocument).document_author = "Some User2"
        self.subdocument.reindexObject()
        self.subsubdocument.reindexObject()
        self.commit_solr()

        # all documents
        view = '@listing?name=documents&columns:list=document_author'
        browser.open(self.subdossier, view=view, headers=self.api_headers)
        all_documents = browser.json['items']
        self.assertIn(self.subdocument.absolute_url(),
                      [item.get("@id") for item in all_documents])
        self.assertIn(self.subsubdocument.absolute_url(),
                      [item.get("@id") for item in all_documents])

        # only documents with specific author
        view = view + '&filters.document_author:record:list={}'.format("Some User")
        browser.open(self.leaf_repofolder, view=view, headers=self.api_headers)
        filtered_documents = browser.json['items']

        self.assertTrue(len(all_documents) > len(filtered_documents) > 0)
        # Make sure that filtering by document_author filtered according to
        # the document_author field
        self.assertItemsEqual(
            [item for item in all_documents if item.get("document_author") == "Some User"],
            filtered_documents)

        # Make sure that document_author is the right user for the expected objects.
        expected_documents = (self.subdocument, )
        self.assertItemsEqual(
            [document.absolute_url() for document in expected_documents],
            [item.get("@id") for item in filtered_documents])

    @browsing
    def test_todos_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=todos',
            'columns=title',
            'columns=responsible',
            'columns=deadline',
            'columns=is_completed',
            'sort_on=deadline',
            'sort_order=ascending',
        ))
        view = '?'.join(('@listing', query_string))

        self.completed_todo.reindexObject()
        self.commit_solr()

        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/todo-1',
                    u'UID': IUUID(self.todo),
                    u'is_completed': False,
                    u'deadline': u'2016-09-01T00:00:00Z',
                    u'responsible': None,
                    u'title': u'Fix user login'},
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/todolist-2/todo-3',
                    u'UID': IUUID(self.completed_todo),
                    u'is_completed': True,
                    u'deadline': u'2016-09-02T00:00:00Z',
                    u'responsible': u'beatrice.schrodinger',
                    u'title': u'Cleanup installation'},
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/todolist-2/todo-2',
                    u'UID': IUUID(self.assigned_todo),
                    u'is_completed': False,
                    u'deadline': u'2016-12-01T00:00:00Z',
                    u'responsible': u'beatrice.schrodinger',
                    u'title': u'Go live'}],
            browser.json['items'])

    @browsing
    def test_todo_lists_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=todo_lists',
            'columns=title',
            'columns=@type',
            'sort_on=getObjPositionInParent',
        ))
        view = '?'.join(('@listing', query_string))

        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/todolist-2',
                    u'@type': u'opengever.workspace.todolist',
                    u'UID': IUUID(self.todolist_introduction),
                    u'title': u'Projekteinf\xfchrung'},
                {
                    u'@id': u'http://nohost/plone/workspaces/workspace-1/todolist-1',
                    u'@type': u'opengever.workspace.todolist',
                    u'UID': IUUID(self.todolist_general),
                    u'title': u'Allgemeine Informationen'}],
            browser.json['items'])

    @browsing
    def test_task_templatefolders_listing(self, browser):
        self.enable_languages()
        self.login(self.regular_user, browser=browser)
        tasktemplatefolder = create(Builder('tasktemplatefolder').titled(u'Sequenzieller Ablauf')
                                    .having(sequence_type='sequential')
                                    .within(self.templates))

        self.commit_solr()

        query_string = '&'.join((
            'name=tasktemplate_folders',
            'columns=title',
            'columns=@type',
            'columns=sequence_type',
            'columns=review_state',
            'sort_on=created',
        ))

        view = '?'.join(('@listing', query_string))
        browser.open(self.templates, view=view,
                     headers={'Accept': 'application/json', 'Accept-Language': 'de-ch'})

        self.assertEqual([{u'@id': u'http://nohost/plone/vorlagen/sequenzieller-ablauf',
                           u'@type': u'opengever.tasktemplates.tasktemplatefolder',
                           u'UID': IUUID(tasktemplatefolder),
                           u'review_state': u'tasktemplatefolder-state-inactiv',
                           u'sequence_type': u'Sequenziell',
                           u'title': u'Sequenzieller Ablauf'},
                          {u'@id': u'http://nohost/plone/vorlagen/verfahren-neuanstellung',
                           u'@type': u'opengever.tasktemplates.tasktemplatefolder',
                           u'UID': u'createspecialtemplates0000000005',
                           u'review_state': u'tasktemplatefolder-state-activ',
                           u'sequence_type': u'Parallel',
                           u'title': u'Verfahren Neuanstellung'}], browser.json['items'])

    @browsing
    def test_sequence_type_facets_are_translated(self, browser):
        self.enable_languages()
        self.login(self.regular_user, browser=browser)
        create(Builder('tasktemplatefolder').titled(u'Sequenzieller Ablauf')
               .having(sequence_type='sequential')
               .within(self.templates))
        self.commit_solr()
        browser.open(self.templates, view='@listing?name=tasktemplate_folders&facets:list=sequence_type',
                     headers={'Accept': 'application/json',
                              'Accept-Language': 'de-ch'})

        self.assertDictEqual(
            {u'sequence_type': {
                u'sequential': {u'count': 1, u'label': u'Sequenziell'},
                u'parallel': {u'count': 1, u'label': u'Parallel'}}},
            browser.json['facets'])

    @browsing
    def test_task_templates_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = 'name=tasktemplates'
        query_string = '&'.join((
            'name=tasktemplates',
            'columns=title',
            'columns=@type',
            'columns=review_state',
            'columns=sequence_type',
        ))

        view = '?'.join(('@listing', query_string))
        browser.open(self.templates, view=view, headers=self.api_headers)
        self.assertEqual([{u'@id': u'http://nohost/plone/vorlagen/verfahren-neuanstellung/'
                                   u'opengever-tasktemplates-tasktemplate',
                           u'@type': u'opengever.tasktemplates.tasktemplate',
                           u'UID': u'createspecialtemplates0000000006',
                           u'review_state': u'tasktemplate-state-active',
                           u'sequence_type': None,
                           u'title': u'Arbeitsplatz einrichten.'}], browser.json['items'])

    @browsing
    def test_dossiertemplates_listing(self, browser):
        self.login(self.regular_user, browser=browser)
        query_string = '&'.join((
            'name=dossiertemplates',
            'columns=title',
            'columns=description',
            'columns=changed',
            'sort_on=changed',
            'sort_order=ascending',
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.templates, view=view, headers=self.api_headers)

        self.assertEqual([
            {
                u'@id': self.dossiertemplate.absolute_url(),
                u'UID': IUUID(self.dossiertemplate),
                u'changed': u'2016-08-31T09:13:33Z',
                u'description': u'Lorem ipsum',
                u'title': u'Bauvorhaben klein'
            },
            {
                u'@id': self.subdossiertemplate.absolute_url(),
                u'UID': IUUID(self.subdossiertemplate),
                u'changed': u'2016-08-31T09:17:33Z',
                u'description': u'',
                u'title': u'Anfragen'
            }
        ], browser.json['items'])

    @browsing
    def test_folder_contents_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=folder_contents',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/todolist-2',
                u'http://nohost/plone/workspaces/workspace-1/todolist-2/todo-3',
                u'http://nohost/plone/workspaces/workspace-1/todolist-2/todo-2',
                u'http://nohost/plone/workspaces/workspace-1/todo-1',
                u'http://nohost/plone/workspaces/workspace-1/todolist-1',
                u'http://nohost/plone/workspaces/workspace-1/meeting-1/agendaitem-1',
                u'http://nohost/plone/workspaces/workspace-1/meeting-1',
                u'http://nohost/plone/workspaces/workspace-1/folder-1',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/document-40',
                u'http://nohost/plone/workspaces/workspace-1/document-39',
                u'http://nohost/plone/workspaces/workspace-1/document-38'
            ],
            [item.get('@id') for item in browser.json['items']])

    @browsing
    def test_folder_contents_listing_filtered_by_depth(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=folder_contents',
            'depth=1',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/todolist-2',
                u'http://nohost/plone/workspaces/workspace-1/todo-1',
                u'http://nohost/plone/workspaces/workspace-1/todolist-1',
                u'http://nohost/plone/workspaces/workspace-1/meeting-1',
                u'http://nohost/plone/workspaces/workspace-1/folder-1',
                u'http://nohost/plone/workspaces/workspace-1/document-39',
                u'http://nohost/plone/workspaces/workspace-1/document-38'
            ],
            [item.get('@id') for item in browser.json['items']])

    @browsing
    def test_filtered_folder_contents_listing(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=folder_contents',
            'filters.portal_type:record:list=opengever.workspace.folder',
            'filters.portal_type:record:list=opengever.document.document',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [
                u'http://nohost/plone/workspaces/workspace-1/folder-1',
                u'http://nohost/plone/workspaces/workspace-1/folder-1/document-40',
                u'http://nohost/plone/workspaces/workspace-1/document-38',
            ],
            [item.get('@id') for item in browser.json['items']])

    @browsing
    def test_folder_contents_listing_works_for_creator_fullname(self, browser):
        self.login(self.workspace_member, browser=browser)
        query_string = '&'.join((
            'name=folder_contents',
            'columns:list=creator_fullname',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(u'Fr\xf6hlich G\xfcnther', browser.json['items'][0].get('creator_fullname'))

    @browsing
    def test_disposition_listing(self, browser):
        self.login(self.records_manager, browser=browser)
        query_string = '&'.join((
            'name=dispositions',
            'columns=sequence',
            'columns=title',
            'columns=modified',
            'columns=UID',
            'columns=review_state',
            'sort_on=created',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(
            [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/disposition-2',
              u'UID': u'createdispositionwithsip00000001',
              u'modified': u'2016-08-31T19:15:33+00:00',
              u'review_state': u'disposition-state-disposed',
              u'title': u'Angebot 30.12.1997'},
             {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/disposition-1',
              u'UID': u'createdisposition000000000000001',
              u'modified': u'2016-08-31T19:11:33+00:00',
              u'review_state': u'disposition-state-in-progress',
              u'title': u'Angebot 31.8.2016'}],
            browser.json['items'])

    @browsing
    def test_dossier_checklist_progress_ordering(self, browser):
        self.login(self.regular_user, browser=browser)

        self.activate_feature('dossier-checklist')
        create(Builder('dossier')
               .within(self.leaf_repofolder)
               .titled(u'Testdossier A')
               .having(
                   checklist={
                       u'items': [
                           {u'title': u'Step 1', u'state': CHECKLIST_CLOSED_STATE},
                           {u'title': u'Step 1', u'state': CHECKLIST_OPEN_STATE},
                       ]
                   }
               )
        )
        create(Builder('dossier')
               .within(self.leaf_repofolder)
               .titled(u'Testdossier B')
               .having(
                   checklist={
                       u'items': [
                           {u'title': u'Step 1', u'state': CHECKLIST_CLOSED_STATE},
                       ]
                   }
               )
        )
        create(Builder('dossier')
               .within(self.leaf_repofolder)
               .titled(u'Testdossier C'))

        self.commit_solr()

        query_string = '&'.join((
            'name=dossiers',
            'sort_on=progress',
            'search=Testdossier',
            'columns:list=title',
            'columns:list=progress',
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.leaf_repofolder, view=view, headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [('Testdossier B', 1.0), ('Testdossier A', 0.5), ('Testdossier C', None)],
            [(item['title'], item['progress']) for item in browser.json['items']])


class TestPloneDossierParticipationsInListingWithRealSolr(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')
    maxDiff = None

    def setUp(self):
        super(TestPloneDossierParticipationsInListingWithRealSolr, self).setUp()
        with self.login(self.manager):
            handler = IParticipationAware(self.dossier)
            handler.add_participation(self.regular_user.getId(),
                                      ['regard', 'participation', 'final-drawing'])
            handler.add_participation(self.dossier_responsible.getId(), ['regard'])

            handler = IParticipationAware(self.subdossier)
            handler.add_participation(self.dossier_responsible.getId(), ['participation'])
            handler.add_participation(self.secretariat_user.getId(), ['final-drawing'])

            handler = IParticipationAware(self.empty_dossier)
            handler.add_participation(self.dossier_responsible.getId(), ['regard'])
            self.commit_solr()

    @skip('Display names should contain username, not userid')
    @browsing
    def test_dossier_participations_fields(self, browser):
        self.login(self.regular_user, browser=browser)

        query_string = '&'.join((
            'name=dossiers',
            'columns=title',
            'columns=participations',
            'columns=participants',
            'columns=participation_roles',
            'filters.UID:record:list={}'.format(IUUID(self.dossier))
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        item = browser.json['items'][0]
        self.assertEqual(self.dossier.absolute_url(), item['@id'])
        self.assertEqual(IUUID(self.dossier), item['UID'])
        self.assertItemsEqual(
            [u'Ziegler Robert (%s)' % self.dossier_responsible.getUserName(),
             u'B\xe4rfuss K\xe4thi (%s)' % self.regular_user.getUserName(),
             u'Any participant'],
            item['participants'])
        self.assertItemsEqual(
            [u'Any role', u'For your information', u'Participation', u'Final signature'],
            item['participation_roles'])
        self.assertItemsEqual(
            [u'Ziegler Robert (%s)|For your information' % self.dossier_responsible.getUserName(),
             u'Ziegler Robert (%s)|Any role' % self.dossier_responsible.getUserName(),
             u'Any participant|For your information',
             u'B\xe4rfuss K\xe4thi (%s)|Participation' % self.regular_user.getUserName(),
             u'B\xe4rfuss K\xe4thi (%s)|For your information' % self.regular_user.getUserName(),
             u'Any participant|Participation',
             u'B\xe4rfuss K\xe4thi (%s)|Any role' % self.regular_user.getUserName(),
             u'B\xe4rfuss K\xe4thi (%s)|Final signature' % self.regular_user.getUserName(),
             u'Any participant|Final signature'],
            item['participations'])

    @browsing
    def test_dossier_participant_filters_combine_with_or(self, browser):
        self.login(self.regular_user, browser=browser)

        participant_filter = 'filters.participants:record:list={}|any-role'
        query_string = '&'.join((
            'name=dossiers',
            participant_filter.format(self.regular_user.getId()),
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier)],
            [item['UID'] for item in browser.json['items']])

        view = view + '&' + participant_filter.format(self.dossier_responsible.getId())
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.subdossier), IUUID(self.empty_dossier)],
            [item['UID'] for item in browser.json['items']])

    @browsing
    def test_dossier_participation_roles_filters_combine_with_or(self, browser):
        self.login(self.regular_user, browser=browser)

        role_filter = 'filters.participation_roles:record:list=any-participant|{}'
        query_string = '&'.join((
            'name=dossiers',
            role_filter.format('final-drawing'),
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.subdossier)],
            [item['UID'] for item in browser.json['items']])

        view = view + '&' + role_filter.format('regard')
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.subdossier), IUUID(self.empty_dossier)],
            [item['UID'] for item in browser.json['items']])

    @browsing
    def test_dossier_participant_and_roles_filters_combine_with_and(self, browser):
        self.login(self.regular_user, browser=browser)

        role_filter = 'filters.participation_roles:record:list=any-participant|{}'
        participant_filter = 'filters.participants:record:list={}|any-role'
        query_string = '&'.join((
            'name=dossiers',
            participant_filter.format(self.dossier_responsible.getId()),
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.subdossier), IUUID(self.empty_dossier)],
            [item['UID'] for item in browser.json['items']])

        view = view + '&' + role_filter.format('regard')
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.empty_dossier)],
            [item['UID'] for item in browser.json['items']])

    @browsing
    def test_cannot_filter_both_by_participations_and_participants(self, browser):
        self.login(self.regular_user, browser=browser)

        participant_filter = 'filters.participants:record:list={}|any-role'
        participation_filter = 'filters.participations:record:list={}|{}'
        query_string = '&'.join((
            'name=dossiers',
            participation_filter.format(self.dossier_responsible.getId(), 'regard'),
            participant_filter.format(self.dossier_responsible.getId()),
        ))
        view = '@listing?{}'.format(query_string)
        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': "Cannot set participations filter together with "
                         "participants or participation_roles filters.",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_cannot_filter_both_by_participations_and_participation_roles(self, browser):
        self.login(self.regular_user, browser=browser)

        role_filter = 'filters.participation_roles:record:list=any-participant|{}'
        participation_filter = 'filters.participations:record:list={}|{}'
        query_string = '&'.join((
            'name=dossiers',
            participation_filter.format(self.dossier_responsible.getId(), 'regard'),
            role_filter.format('regard'),
        ))
        view = '@listing?{}'.format(query_string)
        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(400, browser.status_code)
        self.assertEqual(
            {u'message': "Cannot set participations filter together with "
                         "participants or participation_roles filters.",
             u'type': u'BadRequest'},
            browser.json)

    @browsing
    def test_dossier_participant_and_roles_facets(self, browser):
        """participants facets only include tokens with 'any-role' while
        participation_roles facets only tokens with 'any-participant'.
        Also note that selecting some of the available facets as additional
        filter will lead to an empty result set.
        """
        self.login(self.regular_user, browser=browser)

        role_filter = 'filters.participation_roles:record:list=any-participant|{}'
        participant_filter = 'filters.participants:record:list={}|any-role'
        query_string = '&'.join((
            'name=dossiers',
            'facets:list=participants',
            'facets:list=participation_roles',
            participant_filter.format(self.dossier_responsible.getId())
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.dossier, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.subdossier)],
            [item['UID'] for item in browser.json['items']])
        self.assertItemsEqual(
            ['{}|any-role'.format(self.secretariat_user.getId()),
             '{}|any-role'.format(self.dossier_responsible.getId())],
            browser.json['facets']['participants'].keys())
        self.assertItemsEqual(
            ['any-participant|final-drawing', 'any-participant|participation'],
            browser.json['facets']['participation_roles'].keys())

        view = view + '&' + role_filter.format('final-drawing')
        browser.open(self.dossier, view=view, headers=self.api_headers)
        self.assertEqual(0, browser.json['items_total'])


@requests_mock.Mocker()
class TestKuBDossierParticipationsInListingWithRealSolr(SolrIntegrationTestCase, KuBIntegrationTestCase):

    features = ('bumblebee', 'solr')
    maxDiff = None

    @browsing
    def test_dossier_participations_fields(self, mocker, browser):
        self.login(self.regular_user, browser=browser)

        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.person_jean)
        self.mock_get_by_id(mocker, self.org_ftw)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            self.person_jean, ['participation', 'final-drawing'])
        handler.add_participation(
            self.org_ftw, ['regard'])
        self.commit_solr()

        query_string = '&'.join((
            'name=dossiers',
            'columns=title',
            'columns=participations',
            'columns=participants',
            'columns=participation_roles',
            'filters.UID:record:list={}'.format(IUUID(self.dossier))
        ))
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        item = browser.json['items'][0]
        self.assertEqual(self.dossier.absolute_url(), item['@id'])
        self.assertEqual(IUUID(self.dossier), item['UID'])
        self.assertItemsEqual(
            [u'4Teamwork', u'Dupont Jean', u'Any participant'],
            item['participants'])
        self.assertItemsEqual(
            [u'Any role', u'For your information', u'Participation', u'Final signature'],
            item['participation_roles'])
        self.assertItemsEqual(
            [u'4Teamwork|Any role',
             u'4Teamwork|For your information',
             u'Dupont Jean|Any role',
             u'Dupont Jean|Final signature',
             u'Dupont Jean|Participation',
             u'Any participant|Participation',
             u'Any participant|For your information',
             u'Any participant|Final signature'],
            item['participations'])

    @browsing
    def test_dossier_participant_and_roles_filters(self, mocker, browser):
        self.login(self.regular_user, browser=browser)

        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.person_jean)
        self.mock_get_by_id(mocker, self.org_ftw)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            self.person_jean, ['participation', 'final-drawing', 'regard'])

        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(
            self.org_ftw, ['regard'])

        handler = IParticipationAware(self.meeting_dossier)
        handler.add_participation(
            self.org_ftw, ['final-drawing'])
        self.commit_solr()

        role_filter = 'filters.participation_roles:record:list=any-participant|{}'
        query_string = '&'.join((
            'name=dossiers',
            role_filter.format('regard'))
        )
        view = '@listing?{}'.format(query_string)
        browser.open(self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier), IUUID(self.empty_dossier)],
            [item['UID'] for item in browser.json['items']])

        participant_filter = 'filters.participants:record:list={}|any-role'
        view = view + '&' + participant_filter.format(self.person_jean)
        browser.open(self.repository_root, view=view, headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertItemsEqual(
            [IUUID(self.dossier)],
            [item['UID'] for item in browser.json['items']])


class TestListingSortFirst(SolrIntegrationTestCase):

    def test_build_sort_first_func_string_builds_function_string_correctly(self):
        self.assertEqual(
            'if(or(termfreq(portal_type, type1)), 1, 0) desc',
            ListingGet._build_sort_first_func_string('portal_type', ['type1']))

        self.assertEqual(
            'if(or(termfreq(portal_type, type1),termfreq(portal_type, type2)), 1, 0) desc',
            ListingGet._build_sort_first_func_string('portal_type', ['type1', 'type2']))

    @browsing
    def test_sort_first_raises_error_if_parameter_is_not_a_record(self, browser):
        self.login(self.workspace_member, browser=browser)

        query_string = '&'.join((
            'name=folder_contents',
            'sort_first=type1'
        ))
        view = '?'.join(('@listing', query_string))

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            u'The sort_first parameter needs to be a record.',
            browser.json.get('message'))

    @browsing
    def test_sort_first_raises_error_if_used_with_not_whitelisted_field(self, browser):
        self.login(self.workspace_member, browser=browser)

        not_allowed_field = 'not_whitelisted_field'

        self.assertNotIn(not_allowed_field, ALLOWED_ORDER_GROUP_FIELDS)

        query_string = '&'.join((
            'name=folder_contents',
            'sort_first.{}:record=open'.format(not_allowed_field)
        ))
        view = '?'.join(('@listing', query_string))

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            u'Sort first field not_whitelisted_field is not allowed. Allowed fields are: portal_type.',
            browser.json.get('message'))

    @browsing
    def test_sort_first_raises_error_if_used_with_multiple_field_names(self, browser):
        self.login(self.workspace_member, browser=browser)

        query_string = '&'.join((
            'name=folder_contents',
            'sort_first.portal_type:record=type1',
            'sort_first.review_state:record=state1'
        ))
        view = '?'.join(('@listing', query_string))

        with browser.expect_http_error(reason='Bad Request'):
            browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            u'Exactly one sort_first field is required.',
            browser.json.get('message'))

    @browsing
    def test_sort_first_will_order_a_portal_type_first(self, browser):
        self.login(self.workspace_member, browser=browser)

        query_string = '&'.join((
            'name=folder_contents',
            'sort_first.portal_type:record=opengever.workspace.folder'
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [u'opengever.workspace.folder',
             u'opengever.workspace.todolist',
             u'opengever.workspace.todo',
             u'opengever.workspace.todo',
             u'opengever.workspace.todo',
             u'opengever.workspace.todolist',
             u'opengever.workspace.meetingagendaitem',
             u'opengever.workspace.meeting',
             u'opengever.document.document',
             u'ftw.mail.mail',
             u'opengever.document.document'],
            [item['@type'] for item in browser.json['items']])

    @browsing
    def test_sort_first_by_portal_type_will_order_a_list_of_portal_types_first(self, browser):
        self.login(self.workspace_member, browser=browser)

        query_string = '&'.join((
            'name=folder_contents',
            'sort_first.portal_type:record:list=opengever.workspace.folder',
            'sort_first.portal_type:record:list=opengever.document.document',
        ))
        view = '?'.join(('@listing', query_string))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [u'opengever.workspace.folder',
             u'opengever.document.document',
             u'opengever.document.document',
             u'opengever.workspace.todolist',
             u'opengever.workspace.todo',
             u'opengever.workspace.todo',
             u'opengever.workspace.todo',
             u'opengever.workspace.todolist',
             u'opengever.workspace.meetingagendaitem',
             u'opengever.workspace.meeting',
             u'ftw.mail.mail',
             ],
            [item['@type'] for item in browser.json['items']])

    @browsing
    def test_sort_first_will_order_each_group_by_the_provided_sort_order(self, browser):
        self.login(self.workspace_member, browser=browser)

        query_string = '&'.join((
            'name=folder_contents',
            'columns:list=title',
            'columns:list=@type',
            'sort_on=title',
            'sort_first.portal_type:record:list=opengever.workspace.folder',
            'sort_first.portal_type:record:list=opengever.document.document',
        ))
        view = '?'.join(('@listing', query_string + '&sort_order=asc'))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [(u'Ordnerdokument', u'opengever.document.document'),
             (u'Teamraumdokument', u'opengever.document.document'),
             (u'WS F\xc3lder', u'opengever.workspace.folder'),
             (u'Allgemeine Informationen', u'opengever.workspace.todolist'),
             (u'Besprechung Kl\xe4ranlage', u'opengever.workspace.meeting'),
             (u'Cleanup installation', u'opengever.workspace.todo'),
             (u'Die B\xfcrgschaft', u'ftw.mail.mail'),
             (u'Fix user login', u'opengever.workspace.todo'),
             (u'Genehmigung des Lageberichts', u'opengever.workspace.meetingagendaitem'),
             (u'Go live', u'opengever.workspace.todo'),
             (u'Projekteinf\xfchrung', u'opengever.workspace.todolist')],
            [(item['title'], item['@type']) for item in browser.json['items']])

        view = '?'.join(('@listing', query_string + '&sort_order=reverse'))
        browser.open(self.workspace, view=view, headers=self.api_headers)

        self.assertEqual(
            [(u'WS F\xc3lder', u'opengever.workspace.folder'),
             (u'Teamraumdokument', u'opengever.document.document'),
             (u'Ordnerdokument', u'opengever.document.document'),
             (u'Projekteinf\xfchrung', u'opengever.workspace.todolist'),
             (u'Go live', u'opengever.workspace.todo'),
             (u'Genehmigung des Lageberichts', u'opengever.workspace.meetingagendaitem'),
             (u'Fix user login', u'opengever.workspace.todo'),
             (u'Die B\xfcrgschaft', u'ftw.mail.mail'),
             (u'Cleanup installation', u'opengever.workspace.todo'),
             (u'Besprechung Kl\xe4ranlage', u'opengever.workspace.meeting'),
             (u'Allgemeine Informationen', u'opengever.workspace.todolist')],
            [(item['title'], item['@type']) for item in browser.json['items']])
