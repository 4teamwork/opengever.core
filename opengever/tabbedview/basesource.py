from five import grok
from opengever.tabbedview.filtered_source import FilteredTableSourceMixin
from ftw.table.basesource import BaseTableSource


class GeverTableSource(grok.MultiAdapter,
                       FilteredTableSourceMixin,
                       BaseTableSource):
    """Base table source used for some tables.

    Add support for gever-specific filterlist configuration option, also
    adds support for grok-style directives. It should always be used whenever
    a table-source is required.

    """
    grok.baseclass()
