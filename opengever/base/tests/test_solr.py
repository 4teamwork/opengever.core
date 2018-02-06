from ftw.solr.connection import SolrResponse
from lxml import etree
from opengever.base.solr import OGSolrContentListing
from opengever.base.solr import OGSolrContentListingObject
from opengever.base.solr import OGSolrDocument
from opengever.tabbedview import BaseCatalogListingTab
from opengever.testing import IntegrationTestCase
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
        all_columns = set()
        for tab in tabs:
            try:
                columns = set([c['column'] for c in tab.columns if c['column']])
            except TypeError:
                columns = set()
            for column in columns:
                self.assertIn(
                    column,
                    solr_fields,
                    'Solr schema is missing field {} used in {}.'.format(
                        column, tab))
            all_columns = all_columns.union(columns)

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
