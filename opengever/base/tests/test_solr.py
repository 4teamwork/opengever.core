from ftw.solr.connection import SolrResponse
from lxml import etree
from opengever.base.solr import OGSolrContentListing
from opengever.base.solr import OGSolrContentListingObject
from opengever.base.solr import OGSolrDocument
from opengever.tabbedview import BaseCatalogListingTab
from opengever.testing import IntegrationTestCase
from pkg_resources import get_distribution
from plone import api
import os
import pkg_resources
import unittest


def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield subclass
        for subsubclass in get_subclasses(subclass):
            yield subsubclass


class TestSolr(IntegrationTestCase):

    def test_solr_schema_contains_all_tabbedview_columns(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema'))
        solr_fields = tree.xpath('.//field/@name')
        tabs = get_subclasses(BaseCatalogListingTab)
        for tab in tabs:
            try:
                columns = [c['column'] for c in tab.columns if c['column']]
            except TypeError:
                columns = []
            for column in columns:
                self.assertIn(
                    column,
                    solr_fields,
                    'Solr schema is missing field {} used in {}.'.format(
                        column, tab))

    def test_solr_schema_contains_all_search_options_columns(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema'))
        solr_fields = tree.xpath('.//field/@name')
        tabs = get_subclasses(BaseCatalogListingTab)
        for tab in tabs:
            columns = tab.search_options.keys()
            for column in columns:
                self.assertIn(
                    column,
                    solr_fields,
                    'Solr schema is missing field {} used in search_options '
                    'of {}.'.format(column, tab))

    def test_contentlisting_returns_og_types(self):
        body = """{
            "responseHeader": {"status": 0},
            "response": {
                "numFound": 1,
                "start": 0,
                "docs": [{
                    "UID": "85bed8c49f6d4f8b841693c6a7c6cff1",
                    "Title": "My Item"
                }]
            }
        }"""
        resp = SolrResponse(body=body, status=200)
        listing = OGSolrContentListing(resp)
        self.assertTrue(isinstance(listing[0], OGSolrContentListingObject))
        self.assertTrue(isinstance(listing[0].doc, OGSolrDocument))

    def test_solr_schema_contains_all_new_indexes_and_metadata(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema'))
        solr_fields = tree.xpath('.//field/@name')

        catalog = api.portal.get_tool('portal_catalog')

        # indexes
        CATALOG_ONLY_INDEXES = [
            'Date',
            'Type',
            'after_resolve_jobs_pending',
            'blocked_local_roles',
            'cmf_uid',
            'contactid',
            'date_of_completion',
            'effectiveRange',
            'external_reference',
            'getId',
            'getObjPositionInParent',
            'in_reply_to',
            'is_default_page',
            'is_folderish',
            'meta_type',
            'predecessor',
            'sortable_author',
        ]

        for index in catalog.indexes():
            if index not in CATALOG_ONLY_INDEXES:
                self.assertIn(
                    index, solr_fields,
                    '`{}` is missing in the solr schema fields, or is it a '
                    'catalog only index?'.format(index))

        CATALOG_ONLY_METADATA = [
            'Date',
            'EffectiveDate',
            'ExpirationDate',
            'Type',
            'cmf_uid',
            'contactid',
            'css_icon_class',
            'date_of_completion',
            'exclude_from_nav',
            'getContentType',
            'getId',
            'getRemoteUrl',
            'in_response_to',
            'is_folderish',
            'listCreators',
            'location',
            'meta_type',
            'predecessor',
            'title_de',
            'title_fr',
        ]

        for metadata in catalog.schema():
            if metadata not in CATALOG_ONLY_METADATA:
                self.assertIn(
                    metadata, solr_fields,
                    '`{}` is missing in the solr schema fields, or is it a '
                    'catalog only metadata?'.format(metadata))


class TestOGSolrDocument(unittest.TestCase):

    def test_without_bumblebee_checksum(self):
        doc = OGSolrDocument(data={})
        self.assertEqual(doc.bumblebee_checksum, None)

    def test_with_bumblebee_checksum(self):
        doc = OGSolrDocument(data={'bumblebee_checksum': '123abc'})
        self.assertEqual(doc.bumblebee_checksum, '123abc')

    def test_without_containing_dossier(self):
        doc = OGSolrDocument(data={})
        self.assertEqual(doc.containing_dossier, None)

    def test_with_containing_dossier(self):
        doc = OGSolrDocument(data={'containing_dossier': 'My Dossier'})
        self.assertEqual(doc.containing_dossier, 'My Dossier')

    def test_croppeddescription_returns_snippets(self):
        doc = OGSolrDocument(data={'_snippets_': 'snippets'})
        obj = OGSolrContentListingObject(doc)
        self.assertEqual(obj.CroppedDescription(), 'snippets')

    def test_croppeddescription_without_snippets(self):
        doc = OGSolrDocument(data={'Description': 'My Description'})
        obj = OGSolrContentListingObject(doc)
        self.assertEqual(obj.CroppedDescription(), 'My Description')
