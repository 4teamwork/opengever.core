from itertools import chain
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from opengever.testing import IntegrationTestCase
from plone.testing.zca import _REGISTRIES
from Products.CMFCore.utils import getToolByName
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex


class TestTableSourceConfigs(IntegrationTestCase):

    def test_no_date_indexes_with_falsy_values(self):
        """When sorting a catalog query by a date index containing falsy values,
        it will remove brains with falsy values from the result set.
        It cannot do a correct job in this case because the date index does not
        know whether falsy items need to be inserted at the top or at the bottom.

        The correct approach is to write date indexers which always return a
        datetime object. It may be in the far-future or in the far-past when the
        actual value is not set.
        """
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes_with_falsy_values = []

        for index in catalog._catalog.indexes.values():
            if not isinstance(index, DateIndex):
                continue
            if filter(lambda value: not value, index.uniqueValues()):
                indexes_with_falsy_values.append(index)

        self.assertEquals(
            [], indexes_with_falsy_values,
            'Date indexes are not allowed to contain falsy values.'
            ' Change the indexer so that always returns a datetime object.')

    def test_date_indexes_are_not_custom_sort_indexes(self):
        """ftw.table's catalog source does not let the catalog sort by date
        indexes because it may remove results when the index contains falsy
        values.

        We make sure that we don't have falsy values in our date indexes.
        Therefore we can remove this protection.
        """

        adapters = chain(*(sm.registeredAdapters() for sm in _REGISTRIES))
        adapter_factories = (adapter.factory for adapter in adapters)
        table_source_configs = filter(IGeverCatalogTableSourceConfig.implementedBy,
                                      adapter_factories)
        date_index = 'Products.PluginIndexes.DateIndex.DateIndex'
        bad_configs = filter(lambda cls: date_index in cls.custom_sort_indexes,
                             table_source_configs)
        self.assertEquals([], bad_configs)
