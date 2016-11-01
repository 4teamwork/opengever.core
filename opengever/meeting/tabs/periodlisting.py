from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Period
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


class IPeriodTableSourceConfig(ITableSourceConfig):
    """Marker interface for period table source configs."""


class PeriodListingTab(BaseListingTab):
    implements(IPeriodTableSourceConfig)

    model = Period
    sort_on = 'date_from'
    sort_reverse = True

    @property
    def columns(self):
        return (
            {'column': 'title',
             'column_title': _(u'column_title', default=u'Title'),
             },

            {'column': 'date_from',
             'column_title': _(u'column_date_from', default=u'From'),
             'transform': lambda item, value: item.get_date_from(),
             },

            {'column': 'date_to',
             'column_title': _(u'column_date_to', default=u'To'),
             'transform': lambda item, value: item.get_date_to(),
             },
            )

    def get_base_query(self):
        return Period.query.by_committee(self.context.load_model())


class PeriodTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(PeriodListingTab, Interface)

    searchable_columns = [Period.title]
