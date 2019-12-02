from datetime import datetime
from ftw.bumblebee import get_service_v3
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import Trasher
from plone import api
from urllib import urlencode
import urlparse


class TestSearchEndpoint(IntegrationTestCase):

    def search_catalog(self, context, query):
        catalog = api.portal.get_tool('portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        query['path'] = path
        return [b.getURL() for b in catalog(query)]

    def search_restapi(self, browser, context, query):
        browser.open(
            context,
            view='@search?%s' % urlencode(query),
            headers=self.api_headers)
        return [item['@id'] for item in browser.json['items']]

    @browsing
    def test_able_to_search_for_trashed_docs(self, browser):
        self.login(self.regular_user, browser)

        doc_url = self.document.absolute_url()

        # Guard assertion - both direct catalog searches and REST API
        # should give the same results with no trashed documents
        catalog_results = self.search_catalog(
            self.dossier,
            dict(sort_on='path',
                 portal_type='opengever.document.document'))

        api_results = self.search_restapi(
            browser, self.dossier,
            dict(sort_on='path',
                 portal_type='opengever.document.document'))

        self.assertIn(doc_url, catalog_results)
        self.assertIn(doc_url, api_results)
        self.assertEqual(catalog_results, api_results)

        # Trash self.document - should now disappear from regular results
        Trasher(self.document).trash()

        catalog_results = self.search_catalog(
            self.dossier,
            dict(sort_on='path',
                 portal_type='opengever.document.document'))

        api_results = self.search_restapi(
            browser, self.dossier,
            dict(sort_on='path',
                 portal_type='opengever.document.document'))

        self.assertNotIn(doc_url, catalog_results)
        self.assertNotIn(doc_url, api_results)
        self.assertEqual(catalog_results, api_results)

        # But trashed docs can still be searched for explicitly, both
        # directly via catalog and the REST API @search endpoint
        catalog_results = self.search_catalog(
            self.dossier,
            dict(sort_on='path',
                 portal_type='opengever.document.document',
                 trashed=True))

        api_results = self.search_restapi(
            browser, self.dossier,
            {'sort_on': 'path',
             'portal_type': 'opengever.document.document',
             'trashed:boolean': '1'})

        self.assertEqual([doc_url], catalog_results)
        self.assertEqual([doc_url], api_results)

    @browsing
    def test_can_sort_trashed_docs_by_modified(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2014, 5, 7, 12, 30)) as clock:
            Trasher(self.subsubdocument).trash()
            clock.forward(minutes=5)

            Trasher(self.taskdocument).trash()
            clock.forward(minutes=5)

            Trasher(self.document).trash()
            clock.forward(minutes=5)

            Trasher(self.subdocument).trash()

        expected_order = [
            self.subsubdocument.absolute_url(),
            self.taskdocument.absolute_url(),
            self.document.absolute_url(),
            self.subdocument.absolute_url(),
        ]

        catalog_results = self.search_catalog(
            self.dossier,
            dict(sort_on='modified',
                 portal_type='opengever.document.document',
                 trashed=True))

        api_results = self.search_restapi(
            browser, self.dossier,
            {'sort_on': 'modified',
             'portal_type': 'opengever.document.document',
             'trashed:boolean': '1'})

        self.assertEqual(expected_order, catalog_results)
        self.assertEqual(expected_order, api_results)

    @browsing
    def test_supports_additional_metadata_from_contentlisting_object(self, browser):
        self.activate_feature('bumblebee')

        self.login(self.regular_user, browser)

        view = (
            '@search?path={}&metadata_fields=preview_pdf_url'
            '&metadata_fields=preview_image_url'.format(
                '/'.join(self.document.getPhysicalPath())))

        browser.open(self.dossier, view=view, headers=self.api_headers)

        items = browser.json['items']
        self.assertItemsEqual(
            [u'@id', u'@type', u'title', u'description', u'review_state',
             u'preview_image_url', u'preview_pdf_url'],
            items[0].keys())

        # Use same bumble_id to compare the urls.
        parsed = urlparse.urlparse(items[0]['preview_pdf_url'])
        self.request['bid'] = urlparse.parse_qs(parsed.query)['bid'][0]

        self.assertEqual(
            get_service_v3().get_representation_url(self.document, 'pdf'),
            items[0]['preview_pdf_url'])
        self.assertEqual(
            get_service_v3().get_representation_url(self.document, 'thumbnail'),
            items[0]['preview_image_url'])
