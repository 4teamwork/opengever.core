from ftw.table.catalog_source import CatalogTableSource
from ftw.table.interfaces import ITableSource
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ITableSource)
@adapter(IGeverCatalogTableSourceConfig, Interface)
class GeverCatalogTableSource(FilteredTableSourceMixin, CatalogTableSource):
    """Default catalog tablesource extended with filter functionality.
    """
