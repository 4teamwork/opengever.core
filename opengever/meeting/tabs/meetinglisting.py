from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Meeting
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

        {'column': 'location',
         'column_title': _(u'column_location', default=u'Location')},

        {'column': 'start_datetime',
         'column_title': _(u'column_date', default=u'Date'),
         'transform': lambda item, value: item.get_date()},

        {'column': 'start_time',
         'column_title': _(u'column_from', default=u'From'),
         'transform': lambda item, value: item.get_start_time(),
         'sortable': False},

        {'column': 'end_time',
         'column_title': _(u'column_to', default=u'To'),
         'transform': lambda item, value: item.get_end_time(),
         'sortable': False},
    )

    def get_base_query(self):
        return Meeting.query.filter_by(committee=self.context.load_model())


class MeetingTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(MeetingListingTab, Interface)

    searchable_columns = [Meeting.location]
