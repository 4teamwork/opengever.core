from lxml import etree
from opengever.tabbedview import BaseCatalogListingTab
from opengever.testing import IntegrationTestCase
import os
import pkg_resources


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
