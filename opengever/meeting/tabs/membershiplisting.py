from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Membership
from opengever.tabbedview.browser.base import BaseListingTab
from opengever.tabbedview.browser.sqltablelisting import SqlTableSource
from zope.interface import implements
from zope.interface import Interface


class IMembershipTableSourceConfig(ITableSourceConfig):
    """Marker interface for membership table source configs."""


class MembershipListingTab(BaseListingTab):
    implements(IMembershipTableSourceConfig)

    model = Membership

    columns = (
        {'column': 'member_id',
         'column_title': _(u'column_title', default=u'Title'),
         'transform': lambda item, value: item.title()},

        {'column': 'date_from',
         'column_title': _(u'column_date_from', default=u'Date from'),
         'transform': lambda item, value: item.format_date_from()},

        {'column': 'date_to',
         'column_title': _(u'column_date_to', default=u'Date to'),
         'transform': lambda item, value: item.format_date_to()},

        {'column': 'role',
         'column_title': _(u'column_role', default=u'Role'),
         'transform': lambda item, value: item.role},
    )

    def get_base_query(self):
        return Membership.query.filter_by(committee=self.context.load_model())


class MembershipTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(MembershipListingTab, Interface)

    searchable_columns = []
