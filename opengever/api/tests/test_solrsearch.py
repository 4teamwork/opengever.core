from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.api.solr_query_service import LiveSearchQueryPreprocessingMixin
from opengever.api.solrsearch import SolrSearchGet
from opengever.base.handlers import update_changed_date
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from opengever.testing.integration_test_case import SolrIntegrationTestCase
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from unittest import skip
from unittest import TestCase
from urllib import urlencode
from zope.component import getMultiAdapter
import json


class TestMockSolrSearchGet(IntegrationTestCase):

    features = ['solr']

    @browsing
    def test_default_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json={})

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], 'score desc')

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(self.solr.search.call_args[1]['sort'], None)

    @browsing
    def test_default_portal_type_filter(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json={})

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        plone_utils = getToolByName(self.portal, 'plone_utils')
        types = plone_utils.getUserFriendlyTypes()
        self.assertIn('portal_type:({})'.format(' OR '.join(types)),
                      self.solr.search.call_args[1]['filters'])

    @browsing
    def test_respects_portal_type_filter_if_provided(self, browser):
        self.login(self.regular_user, browser=browser)

        self.solr = self.mock_solr(response_json={})

        url = u'{}/@solrsearch?fq=portal_type:opengever.workspace.meetingagendaitem'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(['portal_type:opengever.workspace.meetingagendaitem',
                          u'path_parent:\\/plone'],
                         self.solr.search.call_args[1]['filters'])


class TestSolrSearchGet(SolrIntegrationTestCase):

    features = ('bumblebee', 'solr')

    @browsing
    def test_raises_bad_request_if_solr_is_not_enabled(self, browser):
        self.deactivate_feature('solr')

        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = u'{}/@solrsearch'.format(self.portal.absolute_url())
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Solr is not enabled on this GEVER installation.',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_internal_error_for_invalid_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(500):
            url = u'{}/@solrsearch?fq=bla:foo'.format(self.portal.absolute_url())
            browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(u'InternalError', browser.json['type'])

    @browsing
    def test_simple_search_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(3, browser.json["items_total"])
        self.assertItemsEqual(
            [item.absolute_url() for item in
             (self.document, self.subdocument, self.offered_dossier_to_archive)],
            [item["@id"] for item in browser.json[u'items']])

    @browsing
    def test_raw_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q.raw=title:Kommentar'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(1, browser.json["items_total"])
        self.assertEqual(self.proposaldocument.absolute_url(),
                         browser.json["items"][0]["@id"])

    @browsing
    def test_fallback_to_default_fields_if_fl_parameter_is_empty(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual([u'review_state',
                               u'title',
                               u'@id',
                               u'UID',
                               u'@type',
                               u'description'],
                              browser.json["items"][0].keys())

    @browsing
    def test_blacklisted_attributes_are_skipped(self, browser):
        self.login(self.regular_user, browser=browser)

        # SearchableText is an unsupported field
        url = u'{}/@solrsearch?fl=SearchableText,allowedRolesAndUsers,getObject,UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual([u'UID', u'Title'],
                              browser.json['items'][0].keys())

    @browsing
    def test_searches_in_context_if_path_is_not_specified(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.subdossier.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        search_on_context = browser.json

        self.assertEqual(5, search_on_context['items_total'])
        for doc in search_on_context['items']:
            self.assertIn(self.subdossier.absolute_url(), doc['@id'])

        url = u'{}/@solrsearch?fq=path:{}'.format(
            self.portal.absolute_url(), self.subdossier.absolute_url_path())
        browser.open(url, method='GET', headers=self.api_headers)
        search_with_path = browser.json

        self.assertEqual(search_on_context['items_total'],
                         search_with_path['items_total'])
        self.assertEqual(search_on_context['items'],
                         search_with_path['items'])

    @browsing
    def test_search_respects_depth_parameter(self, browser):
        self.login(self.regular_user, browser=browser)

        base_url = u'{}/@solrsearch?'\
            'fq=portal_type:opengever.dossier.businesscasedossier'.format(
                self.dossier.absolute_url())
        browser.open(
            "{}&depth=2".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(3, browser.json['items_total'])
        self.assertItemsEqual(
            [self.subdossier.absolute_url(),
             self.subdossier2.absolute_url(),
             self.subsubdossier.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

        browser.open(
            "{}&depth=1".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(2, browser.json['items_total'])
        self.assertItemsEqual(
            [self.subdossier.absolute_url(),
             self.subdossier2.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

        browser.open(
            "{}&depth=0".format(base_url),
            method='GET',
            headers=self.api_headers)

        self.assertEqual(1, browser.json['items_total'])
        self.assertItemsEqual(
            [self.dossier.absolute_url()],
            [doc['@id'] for doc in browser.json['items']])

    @browsing
    def test_filter_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        url = (u'{}/@solrsearch?q=wichtig'.format(
            self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)
        all_items = browser.json["items"]
        self.assertEqual(3, len(all_items))

        url = (u'{}/@solrsearch?q=wichtig&'
               u'fq=portal_type:opengever.document.document'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)
        filtered_items = browser.json["items"]
        self.assertEqual(2, len(filtered_items))
        self.assertItemsEqual(
            [item["@type"] for item in filtered_items
             if item["@type"] == 'opengever.document.document'],
            [item["@type"] for item in filtered_items])

        url = (u'{}/@solrsearch?q=wichtig&fq=portal_type:opengever.document.document&'
               u'fq=path_parent:{}'.format(
                   self.portal.absolute_url(),
                   self.subdossier.absolute_url()
                       .replace(self.portal.absolute_url(), '')
                       .replace("/", "\\/")))
        browser.open(url, method='GET', headers=self.api_headers)
        filtered_items = browser.json["items"]
        self.assertEqual(1, len(filtered_items))
        self.assertEqual(self.subdocument.absolute_url(),
                         filtered_items[0]["@id"])

    @browsing
    def test_returns_json_serialized_solr_docs(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [{u'Title': item.title, u'UID': IUUID(item)}
             for item in (self.document, self.subdocument, self.offered_dossier_to_archive)],
            browser.json[u'items'])

    @browsing
    def test_query_for_external_reference(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=external_reference:qpr-900-9001-\xf7&fl=UID,external_reference'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [{u'UID': IUUID(self.dossier),
              u'external_reference': IDossier(self.dossier).external_reference}],
            browser.json[u'items'])

    @skip("Seems this does not behave very consistently in the moment."
          "Returns empty list in some cases, list of empty strings in others")
    @browsing
    def test_returns_snippets(self, browser):
        """Snippets do not really seem to work??
        """
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=Foo&fl=UID,Title,snippets'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            ['' for i in range(3)],
            [item["snippets"] for item in browser.json[u'items']])

    @browsing
    def test_returns_facets_with_labels(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=true&facet.field=Subject&'
               u'facet.mincount=1'.format(self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)
        facet_counts = browser.json['facet_counts']
        self.assertItemsEqual([u'Subject'], facet_counts.keys())
        self.assertItemsEqual(
            {u'Wichtig': {u'count': 3, u'label': u'Wichtig'},
             u'Subkeyword': {u'count': 1, u'label': u'Subkeyword'}},
            facet_counts[u'Subject'])

    @browsing
    def test_facet_labels_are_transformed_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=on&facet.field=creator&'
               u'facet.field=responsible&facet.mincount=1'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)
        facet_counts = browser.json['facet_counts']

        self.assertItemsEqual([u'creator', 'responsible'], facet_counts.keys())
        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 3, u'label': u'Ziegler Robert'}},
            facet_counts[u'creator'])
        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 1, u'label': u'Ziegler Robert'}},
            facet_counts[u'responsible'])

    @browsing
    def test_using_a_solr_index_as_a_facet_works_properly(self, browser):
        self.login(self.regular_user, browser=browser)

        url = (u'{}/@solrsearch?q=wichtig&facet=on&facet.field=Creator&'
               u'facet.mincount=1'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        facet_counts = browser.json['facet_counts']

        self.assertItemsEqual(
            {u'robert.ziegler': {u'count': 3, u'label': u'robert.ziegler'}},
            facet_counts[u'Creator'])

    @browsing
    def test_facets_support_custom_properties(self, browser):
        self.login(self.regular_user, browser=browser)

        COLORS = [u"Rot", u"Gr\xfcn", u"Blau"]
        LABELS = [u"Alpha", u"Beta", u"Gamma", u"Delta"]

        # Create a property sheet definition with all types
        create(
            Builder("property_sheet_schema")
            .named("mysheet")
            .assigned_to_slots(u"IDocument.default")
            .with_field(
                name=u"color",
                field_type="choice",
                title=u"Color",
                description=u"",
                required=True,
                values=COLORS,
            )
            .with_field(
                name=u"digital",
                field_type="bool",
                title=u"Digital",
                description=u"",
                required=True,
            )
            .with_field(
                name=u"labels",
                field_type="multiple_choice",
                title=u"Labels",
                description=u"",
                required=False,
                values=LABELS,
            )
            .with_field(
                name=u"age",
                field_type="int",
                title=u"Age",
                description=u"",
                required=True,
            )
            .with_field(
                name=u"note",
                field_type="text",
                title=u"Note",
                description=u"",
                required=False,
            )
            .with_field(
                name=u"short_note",
                field_type="textline",
                title=u"Short Note",
                description=u"",
                required=False,
            )
        )

        # Set some properties on documents
        props1 = {
            "custom_properties": {
                "IDocument.default": {
                    "color": u"Gr\xfcn".encode("unicode_escape"),
                    "digital": True,
                    "labels": [u"Alpha"],
                    "age": 42,
                    "note": u"Foo\nBar",
                    "short_note": u"foo bar",
                },
            }
        }

        props2 = {
            "custom_properties": {
                "IDocument.default": {
                    "color": u"Rot".encode("unicode_escape"),
                    "digital": False,
                    "labels": [u"Beta"],
                    "age": 7,
                    "note": u"Hello",
                    "short_note": u"Hello",
                },
            }
        }

        props3 = {
            "custom_properties": {
                "IDocument.default": {
                    "color": u"Rot".encode("unicode_escape"),
                    "digital": False,
                    "labels": [u"Beta", u"Gamma"],
                    "age": 7,
                    "note": u"Hello",
                    "short_note": u"Hello",
                },
            }
        }

        docs = [
            (self.document, props1),
            (self.subdocument, props2),
            (self.subsubdocument, props3),
        ]
        for (obj, props) in docs:
            browser.open(
                obj, method="PATCH", data=json.dumps(props),
                headers=self.api_headers)
        self.commit_solr()

        # Query facets for all custom property fields
        url = (u'{}/@solrsearch?facet=on&'
               u'facet.field=color_custom_field_string&'
               u'facet.field=digital_custom_field_boolean&'
               u'facet.field=labels_custom_field_strings&'
               u'facet.field=age_custom_field_int&'
               u'facet.field=note_custom_field_string&'  # Won't be faceted
               u'facet.field=short_note_custom_field_string&'.format(
                   self.portal.absolute_url()))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIn(u'facet_counts', browser.json)
        facet_counts = browser.json['facet_counts']

        # Fields of type `text` can't be facteted
        self.assertNotIn(u'note_custom_field_string', facet_counts.keys())

        self.assertItemsEqual([
            u'color_custom_field_string',
            u'digital_custom_field_boolean',
            u'labels_custom_field_strings',
            u'age_custom_field_int',
            u'short_note_custom_field_string',
        ], facet_counts.keys())

        expected = {
            u'color_custom_field_string': {
                u'Gr\xfcn': {
                    u'count': 1,
                    u'label': u'Gr\xfcn',
                },
                u'Rot': {
                    u'count': 2,
                    u'label': u'Rot',
                },
            },
            u'digital_custom_field_boolean': {
                u'false': {
                    u'count': 2,
                    u'label': u'false',
                },
                u'true': {
                    u'count': 1,
                    u'label': u'true',
                },
            },
            u'labels_custom_field_strings': {
                u'Alpha': {
                    u'count': 1,
                    u'label': u'Alpha',
                },
                u'Beta': {
                    u'count': 2,
                    u'label': u'Beta',
                },
                u'Gamma': {
                    u'count': 1,
                    u'label': u'Gamma',
                },
            },
            u'age_custom_field_int': {
                u'42': {
                    u'count': 1,
                    u'label': u'42',
                },
                u'7': {
                    u'count': 2,
                    u'label': u'7',
                },
            },
            u'short_note_custom_field_string': {
                u'Hello': {
                    u'count': 2,
                    u'label': u'Hello',
                },
                u'foo bar': {
                    u'count': 1,
                    u'label': u'foo bar',
                },
            },
        }

        self.assertEqual(expected, facet_counts)

    @browsing
    def test_default_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fl=UID,Title'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json["items_total"] > 25)
        self.assertEqual(25, len(browser.json["items"]))
        self.assertEqual(0, browser.json["start"])
        self.assertEqual(25, browser.json["rows"])

    @browsing
    def test_custom_start_and_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fl=UID,Title&rows=100'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        all_items = browser.json["items"]

        url = u'{}/@solrsearch?fl=UID,Title&start=20&rows=10'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        items = browser.json["items"]

        self.assertTrue(len(all_items) > 30)
        self.assertEqual(items, all_items[20:30])

    @browsing
    def test_max_rows(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title&start=0&rows=10000000'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1000, browser.json["rows"])

    @browsing
    def test_default_sort_by_score(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=James%20Bond&fl=Title'.format(
            self.portal.absolute_url())

        self.dossier.title = 'James Bond'
        self.dossier.reindexObject()

        self.subdossier.title = 'Agent 007'
        self.subdossier.description = 'James Bond'
        self.subdossier.reindexObject()

        self.document.title = 'James 007 Bond'
        self.document.reindexObject()

        self.commit_solr()

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual([u'James Bond',
                          u'Agent 007',
                          u'James 007 Bond'],
                         [item["Title"] for item in browser.json["items"]])

    @browsing
    def test_custom_sort(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=wichtig&fl=UID,Title,modified&sort=modified asc'.format(
            self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual([u'2016-08-31T14:07:33+00:00',
                          u'2016-08-31T14:21:33+00:00',
                          u'2016-08-31T19:11:33+00:00'],
                         [item["modified"] for item in browser.json["items"]])

    @browsing
    def test_review_state(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=review_state'.format(
            self.portal.absolute_url(), self.subdossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(
            u'dossier-state-active',
            browser.json['items'][0]['review_state']
        )

    @browsing
    def test_undeterminable_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.task.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIsNone(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_branch_dossier_is_not_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.dossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertFalse(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_subdossier_is_subdossier(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_subdossier'.format(
            self.portal.absolute_url(), self.subdossier.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json['items'][0]['is_subdossier'])

    @browsing
    def test_undeterminable_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.subdocument.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIsNone(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_branch_repositoryfolder_is_not_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.branch_repofolder.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertFalse(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_leaf_repositoryfolder_is_leafnode(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=UID:{}&fl=is_leafnode'.format(
            self.portal.absolute_url(), self.leaf_repofolder.UID())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertTrue(browser.json['items'][0]['is_leafnode'])

    @browsing
    def test_batching(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@solrsearch'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        all_items = browser.json['items']

        # batched no start point
        view = '@solrsearch?b_size=3'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[0:3], browser.json['items'])

        # Next batch
        browser.open(
            browser.json.get('batching').get('next'), headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[3:6], browser.json['items'])

        # Previous batch
        browser.open(
            browser.json.get('batching').get('prev'), headers=self.api_headers)

        self.assertEqual(3, len(browser.json['items']))
        self.assertEqual(all_items[0:3], browser.json['items'])

    @browsing
    def test_breadcrumbs_is_not_included_by_default(self, browser):
        self.login(self.regular_user, browser=browser)

        view = '@solrsearch'
        browser.open(
            self.repository_root, view=view, headers=self.api_headers)
        all_items = browser.json['items']

        self.assertNotIn('breadcrumbs', all_items[0].keys())

    @browsing
    def test_include_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?q=Programm&breadcrumbs=1&fq=portal_type:opengever.document.document'.format(
            self.portal.absolute_url())
        browser.open(url, headers=self.api_headers)
        document = browser.json['items'][0]

        self.assertIn('breadcrumbs', document.keys())
        self.assertEqual(
            [u'description', u'title', u'is_leafnode', u'review_state',
             u'@id', u'@type', u'UID'],
            document['breadcrumbs'][0].keys())
        self.assertEqual(
            [u'http://nohost/plone/ordnungssystem',
             u'http://nohost/plone/ordnungssystem/fuhrung',
             u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
             u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-10',
             u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-10/document-31'],
            [item['@id'] for item in document['breadcrumbs']])

    @browsing
    def test_raises_badrequest_if_breadcrumb_is_enabled_and_b_size_is_higher_than_50(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = u'{}/@solrsearch?q=Programm&breadcrumbs=1&b_size=100'.format(
                self.portal.absolute_url())
            browser.open(url, headers=self.api_headers)

        self.assertEqual(
            {"message": "Breadcrumb flag is only allowed for small batch sizes (max. 50).",
             "type": "BadRequest"},
            browser.json)

    def test_build_group_by_type_function_query_string(self):
        self.assertEqual(
            'if(termfreq(object_provides,opengever.dossier.behaviors.dossier.IDossierMarker),1,0) desc',
            SolrSearchGet._build_group_by_type_function_query_string(['dossiers']))

        self.assertEqual(
            'if(termfreq(object_provides,opengever.repository.interfaces.IRepositoryFolder),3,'
            'if(termfreq(object_provides,opengever.dossier.behaviors.dossier.IDossierMarker),2,'
            'if(termfreq(object_provides,opengever.document.behaviors.IBaseDocument),1,0))) desc',
            SolrSearchGet._build_group_by_type_function_query_string(['repository_folders', 'dossiers', 'documents']))

    @browsing
    def test_group_by_type(self, browser):
        self.login(self.regular_user, browser=browser)

        query_string = '&'.join((
            'rows=15',
            'group_by_type:list=repository_folders',
            'group_by_type:list=proposals',
            'group_by_type:list=dossiers',
        ))
        view = '?'.join(('@solrsearch', query_string))
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(
            [u'opengever.repository.repositoryfolder',
             u'opengever.repository.repositoryfolder',
             u'opengever.repository.repositoryfolder',
             u'opengever.repository.repositoryfolder',
             u'opengever.meeting.proposal',
             u'opengever.meeting.proposal',
             u'opengever.meeting.proposal',
             u'opengever.ris.proposal',
             u'opengever.dossier.businesscasedossier',
             u'opengever.dossier.businesscasedossier',
             u'opengever.dossier.businesscasedossier',
             u'opengever.meeting.meetingdossier',
             u'opengever.meeting.meetingdossier',
             u'opengever.meeting.meetingdossier',
             u'opengever.dossier.businesscasedossier'],
            [item['@type'] for item in browser.json['items']])

    @browsing
    def test_group_by_type_and_sort_by_title(self, browser):
        self.login(self.regular_user, browser=browser)

        query_string = '&'.join((
            'rows=10',
            'sort=sortable_title asc',
            'group_by_type:list=repository_folders',
            'group_by_type:list=proposals',
            'group_by_type:list=dossiers',
        ))
        view = '?'.join(('@solrsearch', query_string))
        browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(
            [(u'1. F\xfchrung', u'opengever.repository.repositoryfolder'),
             (u'1.1. Vertr\xe4ge und Vereinbarungen',
              u'opengever.repository.repositoryfolder'),
             (u'2. Rechnungspr\xfcfungskommission',
              u'opengever.repository.repositoryfolder'),
             (u'3. Spinn\xe4nnetzregistrar', u'opengever.repository.repositoryfolder'),
             (u'Antrag f\xfcr Kreiselbau', u'opengever.meeting.proposal'),
             (u'Initialvertrag f\xfcr Bearbeitung', u'opengever.meeting.proposal'),
             (u'RIS-Proposal', u'opengever.ris.proposal'),
             (u'Vertr\xe4ge', u'opengever.meeting.proposal'),
             (u'2015', u'opengever.dossier.businesscasedossier'),
             (u'2016', u'opengever.dossier.businesscasedossier')],
            [(item['title'], item['@type']) for item in browser.json['items']])

    @browsing
    def test_group_by_type_with_invalid_type_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)

        query_string = '&'.join((
            'group_by_type:list=invalid',
            'group_by_type:list=dossiers',
        ))
        view = '?'.join(('@solrsearch', query_string))

        with browser.expect_http_error(400):
            browser.open(self.portal, view=view, headers=self.api_headers)

        self.assertEqual(u'BadRequest', browser.json['type'])
        self.assertIn(u"group_by_type type 'invalid' is not allowed.", browser.json['message'])

    @browsing
    def test_filter_by_path_parent(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?fq=path_parent:/private/{}'.format(
            self.portal.absolute_url(), self.regular_user.id)

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [
                u'http://nohost/plone/private/%s/dossier-15' % self.regular_user.id,
                u'http://nohost/plone/private/%s' % self.regular_user.id,
                u'http://nohost/plone/private/%s/dossier-14/document-37' % self.regular_user.id,
                u'http://nohost/plone/private/%s/dossier-14' % self.regular_user.id,
                u'http://nohost/plone/private/%s/dossier-14/document-36' % self.regular_user.id,
            ],
            [item.get('@id') for item in browser.json.get('items')])

    @browsing
    def test_filter_by_multiple_path_parents_will_use_an_or_operator(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.portal.absolute_url(),
            '&'.join([
                'fq:list=path_parent:/private/%s' % self.regular_user.id,
                'fq:list=path_parent:/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2'
            ]))

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-24',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4',
                u'http://nohost/plone/private/%s/dossier-15' % self.regular_user.id,
                u'http://nohost/plone/private/%s' % self.regular_user.id,
                u'http://nohost/plone/private/%s/dossier-14/document-37' % self.regular_user.id,
                u'http://nohost/plone/private/%s/dossier-14' % self.regular_user.id,
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4/document-23',
                u'http://nohost/plone/private/%s/dossier-14/document-36' % self.regular_user.id,
            ],
            [item.get('@id') for item in browser.json.get('items')])

    def test_add_path_parent_filters_does_nothing_if_there_is_no_path_parent_filter(self):
        solrsearch = getMultiAdapter((self.portal, self.request), name='GET_application_json_@solrsearch')
        filters = ['title:Lorem Ipsum']
        solrsearch.add_path_parent_filters(filters)

        self.assertEqual(['title:Lorem Ipsum'], filters)

    def test_add_path_parent_filters_replaces_an_existing_path_parent_filter_with_the_internal_phyisical_path(self):
        solrsearch = getMultiAdapter((self.portal, self.request), name='GET_application_json_@solrsearch')
        filters = ['path_parent:/ordnungssystem/dossier\\-1']
        solrsearch.add_path_parent_filters(filters)

        self.assertEqual([u'path_parent:(\\/plone\\/ordnungssystem\\/dossier\\-1)'], filters)

    def test_add_path_parent_filters_connects_multiple_path_parent_filters_with_an_or_operator(self):
        solrsearch = getMultiAdapter((self.portal, self.request), name='GET_application_json_@solrsearch')
        filters = [
            'path_parent:/inbox',
            'path_parent:/private',
        ]
        solrsearch.add_path_parent_filters(filters)

        self.assertEqual(
            [u'path_parent:(\\/plone\\/inbox OR \\/plone\\/private)'], filters)

    def test_add_path_parent_filters_respects_escaped_filter_values(self):
        solrsearch = getMultiAdapter((self.portal, self.request), name='GET_application_json_@solrsearch')
        filters = ['path_parent:\\/inbox']
        solrsearch.add_path_parent_filters(filters)

        self.assertEqual([u'path_parent:(\\/plone\\/inbox)'], filters)

    @browsing
    def test_returns_stats_for_single_field(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.subdossier.absolute_url(),
            'stats=true&stats.field=filesize'
        )
        browser.open(url, method='GET', headers=self.api_headers)

        stats = browser.json['stats']
        self.assertEqual(
            stats,
            {
                u'filesize': {
                    u'count': 3,
                    u'min': 0.0,
                    u'max': 19.0,
                    u'sum': 38.0,
                    u'missing': 2,
                    u'sumOfSquares': 722.0,
                    u'stddev': 10.969655114602888,
                    u'mean': 12.666666666666666
                }
            }
        )

    @browsing
    def test_returns_stats_for_multiple_fields(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.subdossier.absolute_url(),
            'stats=true&stats.field=filesize&stats.field=Creator'
        )
        browser.open(url, method='GET', headers=self.api_headers)

        stats = browser.json['stats']
        self.assertEqual(
            stats,
            {
                u'Creator': {
                    u'count': 5,
                    u'max': u'robert.ziegler',
                    u'min': u'robert.ziegler',
                    u'missing': 0
                },
                u'filesize': {
                    u'count': 3,
                    u'min': 0.0,
                    u'max': 19.0,
                    u'sum': 38.0,
                    u'missing': 2,
                    u'sumOfSquares': 722.0,
                    u'stddev': 10.969655114602888,
                    u'mean': 12.666666666666666
                }
            }
        )

    @browsing
    def test_blacklisted_attributes_stats_are_skipped(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.subdossier.absolute_url(),
            'stats=true&stats.field=_version_&stats.field=allowedRolesAndUsers'
        )
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertIsNone(browser.json.get('stats'))

    @browsing
    def test_fq_with_urls(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.portal.absolute_url(),
            '&'.join([
                'fq:list=@id:{}'.format(self.document.absolute_url()),
                'fq:list=url:{}'.format(self.task.absolute_url())
            ]))

        browser.open(url, method='GET', headers=self.api_headers)
        search_on_context = browser.json

        self.assertEqual(2, search_on_context['items_total'])

    @browsing
    def test_fq_with_url_parents(self, browser):
        self.login(self.administrator, browser=browser)

        url = u'{}/@solrsearch?{}'.format(
            self.portal.absolute_url(),
            '&'.join([
                'fq:list=@id_parent:{}'.format(self.subdossier.absolute_url()),
                'fq:list=url_parent:{}'.format(self.inbox.absolute_url())
            ]))

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertItemsEqual(
            [
                u'http://nohost/plone/eingangskorb/eingangskorb_fa',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/document-12',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/document-13',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-24',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4/document-23'
            ],
            [item['@id'] for item in browser.json['items']])

    @browsing
    def test_fq_with_excluded_url_parents(self, browser):
        self.login(self.administrator, browser=browser)
        ids_filter = 'fq=id:(dossiertemplate-1 OR document-12 OR document-24)'

        url = u'{}/@solrsearch?{}'.format(
            self.portal.absolute_url(),
            '&'.join([ids_filter]))

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertItemsEqual(
            [
                u'http://nohost/plone/vorlagen/dossiertemplate-1',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/document-12',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-24',
            ],
            [item['@id'] for item in browser.json['items']])

        url = u'{}/@solrsearch?{}'.format(
            self.portal.absolute_url(),
            '&'.join([
                ids_filter,
                'fq:list=-@id_parent:{}'.format(self.templates.absolute_url()),
                'fq:list=-url_parent:{}'.format(self.inbox.absolute_url())
            ]))

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertItemsEqual(
            [
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-24',
            ],
            [item['@id'] for item in browser.json['items']])

    @browsing
    def test_search_default_operator_is_and(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Banane"
        self.document.reindexObject(idxs=["Title", "modified"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title", "modified"])
        self.subsubdocument.title = "Taktische Banane und Apfel"
        self.subsubdocument.reindexObject(idxs=["Title", "modified"])
        self.empty_document.title = "Banane und Apfel Strudel"
        self.empty_document.reindexObject(idxs=["Title", "modified"])
        self.commit_solr()

        url = u'{}/@solrsearch?q=banane'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(4, browser.json["items_total"])
        self.assertItemsEqual(
            [item.absolute_url() for item in (self.subdocument, self.document,
                                              self.subsubdocument, self.empty_document)],
            [item["@id"] for item in browser.json[u'items']])

        url = u'{}/@solrsearch?q=banane taktisch'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(2, browser.json["items_total"])
        self.assertItemsEqual(
            [self.subdocument.absolute_url(), self.subsubdocument.absolute_url()],
            [item["@id"] for item in browser.json[u'items']])

        url = u'{}/@solrsearch?q=banane taktisch apfel'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(1, browser.json["items_total"])
        self.assertItemsEqual(
            [self.subsubdocument.absolute_url()],
            [item["@id"] for item in browser.json[u'items']])

        url = u'{}/@solrsearch?q=banane taktisch apfel strudel'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(0, browser.json["items_total"])

    @browsing
    def test_search_sorts_recently_modified_docs_first(self, browser):
        self.login(self.regular_user, browser=browser)

        with freeze(datetime.today() - timedelta(300)):
            self.document.title = "Banane"
            update_changed_date(self.document, None)
            self.document.reindexObject(idxs=["Title"])

        with freeze(datetime.today() - timedelta(1)):
            self.subdocument.title = "Banane"
            update_changed_date(self.subdocument, None)
            self.subdocument.reindexObject(idxs=["Title"])

        with freeze(datetime.today() - timedelta(50)):
            self.subsubdocument.title = "Banane"
            update_changed_date(self.subsubdocument, None)
            self.subsubdocument.reindexObject(idxs=["Title"])

        self.commit_solr()

        url = u'{}/@solrsearch?q=Title:banane'.format(self.portal.absolute_url())
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(3, browser.json["items_total"])
        self.assertEqual(
            [item.absolute_url() for item in
             (self.subdocument, self.subsubdocument, self.document)],
            [item["@id"] for item in browser.json[u'items']])

        with freeze(datetime.today()):
            update_changed_date(self.document, None)

        self.commit_solr()
        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(
            [item.absolute_url() for item in
             (self.document, self.subdocument, self.subsubdocument)],
            [item["@id"] for item in browser.json[u'items']])

    @browsing
    def test_get_related_and_contained_documents(self, browser):
        self.login(self.regular_user, browser=browser)

        # Create document inside subtask and modify its related items
        document = create(Builder("document").within(self.subtask))
        self.set_related_items(self.subtask, [self.subdocument, self.mail_eml])
        self.subtask.reindexObject()
        self.commit_solr()

        url = u'{}/@solrsearch?fl=UID,related_items,portal_type&fq=path_parent:{}'.format(
            self.portal.absolute_url(), self.task.absolute_url()
                .replace(self.portal.absolute_url(), '').replace("/", "\\/"))
        browser.open(url, method='GET', headers=self.api_headers)

        related_items = set()
        for item in browser.json["items"]:
            if item["portal_type"] == "opengever.task.task" and item["related_items"]:
                related_items.update({uid for uid in item["related_items"]})
            elif item["portal_type"] in ['opengever.document.document', 'opengever.mail.mail']:
                related_items.add(item["UID"])

        url = u'{}/@solrsearch?fl=UID,Title&fq=UID:({})'.format(
            self.portal.absolute_url(), " OR ".join(related_items))
        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(5, browser.json["items_total"])
        self.assertItemsEqual(
            [item.UID() for item in
             (self.document, self.taskdocument, self.subdocument, document, self.mail_eml)],
            [item["UID"] for item in browser.json[u'items']])


class TestSolrSearchPost(SolrIntegrationTestCase):
    """The POST endpoint should behave exactly the same as the GET endpoint. We do not
    copy all the tests of 'TestSolrSearchGet' but rewrite the most important ones.
    """
    features = ('bumblebee', 'solr')

    @browsing
    def test_raises_bad_request_if_solr_is_not_enabled(self, browser):
        self.deactivate_feature('solr')

        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = u'{}/@solrsearch'.format(self.portal.absolute_url())
            browser.open(url, method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'message': u'Solr is not enabled on this GEVER installation.',
             u'type': u'BadRequest'}, browser.json)

    @browsing
    def test_raises_internal_error_for_invalid_queries(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(500):
            url = u'{}/@solrsearch'.format(self.portal.absolute_url())
            browser.open(url, method='POST', data=json.dumps({'fq': 'foo:bar'}), headers=self.api_headers)

        self.assertEqual(u'InternalError', browser.json['type'])

    @browsing
    def test_simple_search_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='POST',
                     data=json.dumps({'q': 'wichtig'}),
                     headers=self.api_headers)

        self.assertEqual(3, browser.json["items_total"])
        self.assertItemsEqual(
            [item.absolute_url() for item in
             (self.document, self.subdocument, self.offered_dossier_to_archive)],
            [item["@id"] for item in browser.json[u'items']])

    @browsing
    def test_raw_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='POST',
                     data=json.dumps({'q.raw': 'title:Kommentar'}),
                     headers=self.api_headers)

        self.assertEqual(1, browser.json["items_total"])
        self.assertEqual(self.proposaldocument.absolute_url(),
                         browser.json["items"][0]["@id"])

    @browsing
    def test_fq_with_multiple_filters(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '{}/@solrsearch'.format(self.portal.absolute_url())
        payload = {
            'q': 'wichtig',
            'fq': [
                'portal_type:opengever.document.document OR ftw.mail.mail',
                'path_parent:{}'.format(
                    self.subdossier.absolute_url()
                        .replace(self.portal.absolute_url(), '')
                        .replace("/", "\\/"))
            ]
        }

        browser.open(url, method='POST', data=json.dumps(payload), headers=self.api_headers)
        filtered_items = browser.json["items"]
        self.assertEqual(1, len(filtered_items))
        self.assertEqual(self.subdocument.absolute_url(),
                         filtered_items[0]["@id"])

    @browsing
    def test_dotted_queries(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.subdossier.absolute_url())
        payload = {'stats': True, 'stats.field': 'filesize'}
        browser.open(url, method='POST', data=json.dumps(payload), headers=self.api_headers)

        stats = browser.json['stats']
        self.assertEqual(
            stats,
            {
                u'filesize': {
                    u'count': 3,
                    u'min': 0.0,
                    u'max': 19.0,
                    u'sum': 38.0,
                    u'missing': 2,
                    u'sumOfSquares': 722.0,
                    u'stddev': 10.969655114602888,
                    u'mean': 12.666666666666666
                }
            }
        )

    @browsing
    def test_fl_query(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        payload = {'fl': 'UID,Title'}
        browser.open(url, method='POST', data=json.dumps(payload), headers=self.api_headers)

        self.assertItemsEqual([u'UID', u'Title'],
                              browser.json['items'][0].keys())

    @browsing
    def test_fq_with_urls(self, browser):
        self.login(self.regular_user, browser=browser)

        url = u'{}/@solrsearch'.format(self.dossier.absolute_url())
        payload = {
            'fq': [
                '@id:{}'.format(self.document.absolute_url()),
                'url:{}'.format(self.task.absolute_url())
            ]
        }
        browser.open(url, method='POST', data=json.dumps(payload), headers=self.api_headers)
        search_on_context = browser.json

        self.assertEqual(2, search_on_context['items_total'])

    @browsing
    def test_fq_with_url_parents(self, browser):
        self.login(self.administrator, browser=browser)

        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        payload = {
            'fq': [
                '@id_parent:{}'.format(self.subdossier.absolute_url()),
                'url_parent:{}'.format(self.inbox.absolute_url())
            ]
        }
        browser.open(url, method='POST', data=json.dumps(payload), headers=self.api_headers)
        self.assertItemsEqual(
            [
                u'http://nohost/plone/eingangskorb/eingangskorb_fa',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/document-12',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1',
                u'http://nohost/plone/eingangskorb/eingangskorb_fa/forwarding-1/document-13',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-24',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4',
                u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4/document-23'
            ],
            [item['@id'] for item in browser.json['items']])


class TestSolrLiveSearchGet(SolrIntegrationTestCase):

    features = ('solr', )

    def solr_search(self, browser, query):
        url = u'{}/@solrsearch?{}'.format(self.portal.absolute_url(),
                                          urlencode(query))
        browser.open(url, method='GET', headers=self.api_headers)
        return browser.json

    def solr_livesearch(self, browser, query):
        url = u'{}/@solrlivesearch?{}'.format(self.portal.absolute_url(),
                                              urlencode(query))
        browser.open(url, method='GET', headers=self.api_headers)
        return browser.json

    @browsing
    def test_livesearch_adds_wildcard(self, browser):
        self.login(self.regular_user, browser=browser)

        query = {"q": "Kreis"}
        search = self.solr_search(browser, query)
        self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Antrag f\xfcr Kreiselbau',
             u'Antrag f\xfcr Kreiselbau'],
            [item["title"] for item in livesearch["items"]])

        query = {"q": "Kreiselbau"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, search["items_total"])
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Antrag f\xfcr Kreiselbau',
             u'Antrag f\xfcr Kreiselbau'],
            [item["title"] for item in search["items"]])

    @browsing
    def test_livesearch_adds_wildcard_to_each_term(self, browser):
        self.login(self.regular_user, browser=browser)

        query = {"q": "Title:an kr"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])

        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Antrag f\xfcr Kreiselbau',
             u'Antrag f\xfcr Kreiselbau'],
            [item["title"] for item in livesearch["items"]])

    @browsing
    def test_livesearch_ignores_capitalization(self, browser):
        self.login(self.regular_user, browser=browser)

        query = {"q": "Title:aNtrAg KreiS"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Antrag f\xfcr Kreiselbau',
             u'Antrag f\xfcr Kreiselbau'],
            [item["title"] for item in livesearch["items"]])

    @browsing
    def test_livesearch_preserves_negative_queries(self, browser):
        self.login(self.regular_user, browser=browser)

        query = {"q": "Title:Antrag -kreiselbau"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(0, livesearch["items_total"])

    @browsing
    def test_livesearch_handles_operators(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Apfel"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "Taktische Banane und Apfel"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.empty_document.title = "Banane und Apfel"
        self.empty_document.reindexObject(idxs=["Title"])
        self.commit_solr()

        # default operator is and
        query = {"q": "Taktische Banane Apfel"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])

        query = {"q": "Taktische AND Banane AND Apfel"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])

        query = {"q": "Taktische && Banane && Apfel"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])

        query = {"q": "Taktische OR Banane"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(3, livesearch["items_total"])

        # For some reason that does not work and is treated as AND
        query = {"q": "Taktische || Banane"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])

        # With a combination of operators things become fishy,
        # probably because mm default depends on the operators and
        # edismax might try to do its own magic to counter that.
        query = {"q": "Apfel AND Banane OR Taktische"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(3, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische Banane und Apfel', u'Banane und Apfel', u'Apfel'],
            [item["title"] for item in livesearch[u'items']])

        query = {"q": "Banane OR Apfel AND Taktische"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische Banane und Apfel'],
            [item["title"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_handles_for_hyphenated_terms(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "md-103"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "md-104"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "md-105"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "md-103 or md-104"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'md-103', u'md-104'],
            [item["title"] for item in livesearch[u'items']])

    @browsing
    def test_handles_underscores(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "vorbereitung_103"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "vorbereitung_104"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "nachbearbeitung_104"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "104"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'vorbereitung_104', u'nachbearbeitung_104'],
            [item["title"] for item in livesearch[u'items']])

        query = {"q": "vorbereitung"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'vorbereitung_103', u'vorbereitung_104'],
            [item["title"] for item in livesearch[u'items']])

        query = {"q": '"vorbereitung_104"'}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [u'vorbereitung_104'],
            [item["title"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_handles_brackets(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Apfel"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "Taktische Banane und Apfel"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.empty_document.title = "Banane und Apfel"
        self.empty_document.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "(Apfel AND Banane) OR Taktische"}
        livesearch = self.solr_livesearch(browser, query)

        self.assertEqual(3, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische Banane und Apfel', u'Taktische Banane', u'Banane und Apfel'],
            [item["title"] for item in livesearch[u'items']])

        query = {"q": "(Apfel OR Banane) AND Taktische"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische Banane und Apfel', u'Taktische Banane'],
            [item["title"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_preserves_phrases(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Banane Taktische"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": '"Taktische Banane"'}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [self.subdocument.absolute_url()],
            [item["@id"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_does_not_preserve_unfinished_phrases(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Banane Taktische"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "Taktische Bana"}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [self.document.absolute_url(), self.subdocument.absolute_url()],
            [item["@id"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_preserves_phrase_exclusion(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "Banane Taktische"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": 'banane -"Taktische Banane"'}
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [self.document.absolute_url()],
            [item["@id"] for item in livesearch[u'items']])

    @browsing
    def test_livesearch_handles_hyphens(self, browser):
        self.login(self.regular_user, browser=browser)
        self.document.title = "Taktische"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische-Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "Taktische-Fantastische-Banane"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        # First term does not get a wildcard appended
        query = {"q": "Title:takt-ba"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(0, livesearch["items_total"])

        query = {"q": "Title:taktische-banane"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(2, search["items_total"])
        self.assertItemsEqual(
            [u'Taktische-Banane', u'Taktische-Fantastische-Banane'],
            [item["title"] for item in search["items"]])
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische-Banane', u'Taktische-Fantastische-Banane'],
            [item["title"] for item in livesearch["items"]])

        for query in [{"q": "Title:takt*-ba"},
                      {"q": "Title:taktische-ba"}]:
            search = self.solr_search(browser, query)
            livesearch = self.solr_livesearch(browser, query)
            self.assertEqual(0, search["items_total"])
            self.assertEqual(2, livesearch["items_total"])
            self.assertItemsEqual(
                [u'Taktische-Banane', u'Taktische-Fantastische-Banane'],
                [item["title"] for item in livesearch["items"]])

        for query in [{"q": "Title:fanta"},
                      {"q": "Title:fantastische-ban"}]:
            search = self.solr_search(browser, query)
            livesearch = self.solr_livesearch(browser, query)
            self.assertEqual(0, search["items_total"])
            self.assertEqual(1, livesearch["items_total"])
            self.assertItemsEqual(
                [u'Taktische-Fantastische-Banane'],
                [item["title"] for item in livesearch["items"]])

    @browsing
    def test_livesearch_splits_terms_at_other_special_characters(self, browser):
        self.login(self.regular_user, browser=browser)
        self.document.title = "Taktische"
        self.document.reindexObject(idxs=["Title"])
        self.subdocument.title = "Taktische/Banane"
        self.subdocument.reindexObject(idxs=["Title"])
        self.subsubdocument.title = "Taktische?Banane"
        self.subsubdocument.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "Title:taktische/ba"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische/Banane', "Taktische?Banane"],
            [item["title"] for item in livesearch["items"]])

        query = {"q": "Title:taktische?ba"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Taktische/Banane', "Taktische?Banane"],
            [item["title"] for item in livesearch["items"]])

    @browsing
    def test_livesearch_handles_trailing_special_characters(self, browser):
        self.login(self.regular_user, browser=browser)
        self.document.title = "dotted.title.without.spaces"
        self.document.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "dotted.title."}
        self.assertEqual(1, self.solr_search(browser, query)["items_total"])
        self.assertEqual(1, self.solr_livesearch(browser, query)["items_total"])

        self.document.title = "dotted. title. with. spaces"
        self.document.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "dotted. title."}
        self.assertEqual(1, self.solr_search(browser, query)["items_total"])
        self.assertEqual(1, self.solr_livesearch(browser, query)["items_total"])

        self.document.title = "dashed-title-without-spaces"
        self.document.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "dashed-title-"}
        self.assertEqual(1, self.solr_search(browser, query)["items_total"])
        self.assertEqual(1, self.solr_livesearch(browser, query)["items_total"])

        self.document.title = "dashed- title- with- spaces"
        self.document.reindexObject(idxs=["Title"])
        self.commit_solr()

        query = {"q": "dashed- title-"}
        self.assertEqual(1, self.solr_search(browser, query)["items_total"])
        self.assertEqual(1, self.solr_livesearch(browser, query)["items_total"])

    @browsing
    def test_stemming_does_not_work_in_live_search_but_it_does_not_matter(self, browser):
        """As stemming happened during indexing, and as we keep also the whole
        token, it does not matter that stemming does not happen during query.
        """
        self.login(self.regular_user, browser=browser)

        query = {"q": "Title:runde"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)

        self.assertEqual(1, search["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [item["title"] for item in search["items"]])
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [item["title"] for item in livesearch["items"]])

        query = {"q": "Title:vorstellungsrunde"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)

        self.assertEqual(1, search["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [item["title"] for item in search["items"]])
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern'],
            [item["title"] for item in livesearch["items"]])

        query = {"q": "Title:arbeit"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)

        self.assertEqual(4, search["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern',
             u'Mitarbeiter Dossier generieren',
             u'Arbeitsplatz vorbereiten',
             u'Arbeitsplatz einrichten.'],
            [item["title"] for item in search["items"]])
        self.assertEqual(4, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Vorstellungsrunde bei anderen Mitarbeitern',
             u'Mitarbeiter Dossier generieren',
             u'Arbeitsplatz vorbereiten',
             u'Arbeitsplatz einrichten.'],
            [item["title"] for item in livesearch["items"]])

    @browsing
    def test_querying_sequence_number(self, browser):
        self.login(self.regular_user, browser=browser)
        query = {"q": "14", "fl": "sequence_number"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        # the one with sequence number 20 has reference Client1 1.1 / 14
        self.assertEqual(4, livesearch["items_total"])
        self.assertItemsEqual(
            [14, 14, 14, 20],
            [item["sequence_number"] for item in livesearch["items"]])
        self.assertEqual(4, search["items_total"])
        self.assertItemsEqual(
            [14, 14, 14, 20],
            [item["sequence_number"] for item in search["items"]])

    @browsing
    def test_querying_reference_number(self, browser):
        self.login(self.regular_user, browser=browser)
        query = {"q": "Client1 1.1 / 14", "fl": "@id,reference_number"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)

        self.assertEqual(2, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Client1 1.1 / 14', u'Client1 1.1 / 1 / 14'],
            [item["reference_number"] for item in livesearch["items"]])
        self.assertEqual(2, search["items_total"])
        self.assertItemsEqual(
            [u'Client1 1.1 / 14', u'Client1 1.1 / 1 / 14'],
            [item["reference_number"] for item in search["items"]])

    @browsing
    def test_querying_reference_number_grouped_by_three(self, browser):
        self.login(self.regular_user, browser=browser)
        api.portal.set_registry_record(
            name='formatter', value='grouped_by_three',
            interface=IReferenceNumberSettings)
        self.leaf_repofolder.reindexObject()
        self.branch_repofolder.reindexObject()
        self.repository_root.reindexObject()
        self.dossier.reindexObject()
        self.subdossier.reindexObject()
        self.subsubdossier.reindexObject()
        self.document.reindexObject()
        self.subdocument.reindexObject()
        self.subsubdocument.reindexObject()
        self.commit_solr()

        query = {"q": "Client1 11-1.1.1-23", "fl": "@id,reference_number"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, livesearch["items_total"])
        self.assertItemsEqual(
            [u'Client1 11-1.1.1-23'],
            [item["reference_number"] for item in livesearch["items"]])
        self.assertEqual(1, search["items_total"])
        self.assertItemsEqual(
            [u'Client1 11-1.1.1-23'],
            [item["reference_number"] for item in search["items"]])

    @browsing
    def test_livesearch_handles_alphanumeric_tokens(self, browser):
        self.login(self.regular_user, browser=browser)

        self.document.title = "4A.BE.2301-43B/C32"
        self.document.reindexObject(idxs=["Title"])
        self.commit_solr()

        queries = [{"q": "4A.BE.2301-43B/C32"},
                   {"q": "4A.BE.2301-43"},
                   {"q": "4A.BE"},
                   {"q": "2301"},
                   {"q": "BE.2301"},
                   {"q": "43B"},
                   {"q": "B/C"}]
        for query in queries:
            search = self.solr_search(browser, query)
            livesearch = self.solr_livesearch(browser, query)
            self.assertEqual(1, search["items_total"])
            self.assertEqual(1, livesearch["items_total"])
            self.assertItemsEqual(
                [self.document.absolute_url()],
                [item["@id"] for item in livesearch[u'items']])
            self.assertItemsEqual(
                [self.document.absolute_url()],
                [item["@id"] for item in search[u'items']])

    @browsing
    def test_querying_filenames(self, browser):
        self.login(self.regular_user, browser=browser)
        self.document.title = "20221121_some_file-name"
        self.document.reindexObject(idxs=["Title", "filename"])
        self.commit_solr()

        # partial filename is only found with livesearch
        query = {"q": "202211"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(1, livesearch["items_total"])

        query = {"q": "20221121_some"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, search["items_total"])
        self.assertEqual(1, livesearch["items_total"])

        # full filename without extension is found by both
        query = {"q": "20221121_some_file-name"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, search["items_total"])
        self.assertEqual(1, livesearch["items_total"])

        # full filename with extension is not found by any, as we do not
        # not search the filename field, only the title field.
        query = {"q": "20221121_some_file-name.docx"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(0, search["items_total"])
        self.assertEqual(0, livesearch["items_total"])

        # when specifically searching the filename field, splitting at
        # hyphens can come in the way in the livesearch
        query = {"q": "filename:20221121_some_file-name.docx"}
        search = self.solr_search(browser, query)
        livesearch = self.solr_livesearch(browser, query)
        self.assertEqual(1, search["items_total"])
        self.assertEqual(0, livesearch["items_total"])

    @browsing
    def test_only_preprocess_query(self, browser):
        self.login(self.regular_user, browser=browser)
        query = {"q": "some word-with-hyhpen", "only_preprocess_query": "true"}
        self.solr_livesearch(browser, query)
        self.assertEqual(
            {u'preprocessed_query': u'some* (word with hyhpen*)'},
            browser.json)


class TestSolrLiveSearchPost(TestSolrLiveSearchGet):

    def solr_search(self, browser, query):
        url = u'{}/@solrsearch'.format(self.portal.absolute_url())
        browser.open(url, method='POST', data=json.dumps(query), headers=self.api_headers)
        return browser.json

    def solr_livesearch(self, browser, query):
        url = u'{}/@solrlivesearch'.format(self.portal.absolute_url())
        browser.open(url, method='POST', data=json.dumps(query), headers=self.api_headers)
        return browser.json


class TestSolrLiveSearchQueryPreprocessing(TestCase):

    def test_preprocessing_handles_trailing_wildcard(self):
        preprocessor = LiveSearchQueryPreprocessingMixin()
        self.assertEqual("*", preprocessor.preprocess_query("*"))
        self.assertEqual("(my* hyphenated word*)", preprocessor.preprocess_query("my*-hyphenated-word*"))
        self.assertEqual("my* oh* my*", preprocessor.preprocess_query("my* oh my*"))

    def test_preprocessing_handles_brakets(self):
        preprocessor = LiveSearchQueryPreprocessingMixin()
        self.assertEqual("(this* OR that*) (even* OR more*)",
                         preprocessor.preprocess_query("(this OR that) (even OR more)"))
        self.assertEqual("(this* AND that*) OR (even* AND more*)",
                         preprocessor.preprocess_query("(this AND that) OR (even AND more)"))
        self.assertEqual("((this* that*) OR another*) (even* more*))",
                         preprocessor.preprocess_query("((this that) OR another) (even more))"))
        self.assertEqual("(hyphenated word*) OR another*",
                         preprocessor.preprocess_query("hyphenated-word OR another"))

    def test_preprocessing_keeps_single_special_chars(self):
        preprocessor = LiveSearchQueryPreprocessingMixin()
        self.assertEqual("this* - that*", preprocessor.preprocess_query("this - that"))
        self.assertEqual("this* _ that*", preprocessor.preprocess_query("this _ that"))
        self.assertEqual("this* + that*", preprocessor.preprocess_query("this + that"))
        self.assertEqual("this* @ that*", preprocessor.preprocess_query("this @ that"))
        self.assertEqual("this* % that*", preprocessor.preprocess_query("this % that"))
        self.assertEqual("this* \\ that*", preprocessor.preprocess_query("this \\ that"))
        self.assertEqual("this* < that*", preprocessor.preprocess_query("this < that"))
        self.assertEqual("this* > that*", preprocessor.preprocess_query("this > that"))
        self.assertEqual("this* | that*", preprocessor.preprocess_query("this | that"))
        self.assertEqual("this* = that*", preprocessor.preprocess_query("this = that"))
        self.assertEqual("this* ? that*", preprocessor.preprocess_query("this ? that"))
        self.assertEqual("this* * that*", preprocessor.preprocess_query("this * that"))
        self.assertEqual("this* & that*", preprocessor.preprocess_query("this & that"))
        self.assertEqual("this* ( that*", preprocessor.preprocess_query("this ( that"))
        self.assertEqual("this* ) that*", preprocessor.preprocess_query("this ) that"))
        self.assertEqual("this* ! that*", preprocessor.preprocess_query("this ! that"))
        self.assertEqual("this* ' that*", preprocessor.preprocess_query("this ' that"))

    def test_preprocessing_appends_wildcard_to_single_alphanumerical_chars(self):
        preprocessor = LiveSearchQueryPreprocessingMixin()
        self.assertEqual("this* a* that*", preprocessor.preprocess_query("this a that"))
        self.assertEqual("this* 4* that*", preprocessor.preprocess_query("this 4 that"))
