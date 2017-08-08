from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from ftw.table.basesource import BaseTableSource


class GeverTableSource(FilteredTableSourceMixin, BaseTableSource):
    """Base table source used for some tables.

    Add support for gever-specific filterlist configuration option.
    It should always be used whenever a table-source is required.
    """
