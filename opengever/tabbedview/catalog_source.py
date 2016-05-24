from five import grok
from ftw.table.catalog_source import CatalogTableSource
from ftw.table.interfaces import ITableSource
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from zope.interface import Interface
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin


class GeverCatalogTableSource(grok.MultiAdapter, FilteredTableSourceMixin, CatalogTableSource):

    grok.implements(ITableSource)
    grok.adapts(IGeverCatalogTableSourceConfig, Interface)
