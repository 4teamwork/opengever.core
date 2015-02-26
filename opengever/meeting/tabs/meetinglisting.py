from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting.model import Meeting
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


class IMeetingTableSourceConfig(ITableSourceConfig):
    """Marker interface for meeting table source configs."""


class MeetingListingTab(BaseListingTab):
    implements(IMeetingTableSourceConfig)

    model = Meeting

    columns = (
        {'column': 'committee_id',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.get_link()},

        {'column': 'date',
         'column_title': _(u'column_date', default=u'Date'),
         'transform': lambda item, value: item.get_date()},

        {'column': 'start_time',
         'column_title': _(u'column_start_time', default=u'Start Time'),
         'transform': lambda item, value: item.get_start_time()},

        {'column': 'end_time',
         'column_title': _(u'column_end_time', default=u'End Time'),
         'transform': lambda item, value: item.get_end_time()},
        )

    def get_base_query(self):
        return Meeting.query.filter_by(committee=self.context.load_model())


class MeetingTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(MeetingListingTab, Interface)

    searchable_columns = [Meeting.location]
