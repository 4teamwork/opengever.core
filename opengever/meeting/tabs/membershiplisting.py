from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.meeting import _
from opengever.meeting.model import Membership
from opengever.tabbedview import FilteredListingTab
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview import SqlTableSource
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
from opengever.meeting.model import Member


class IMembershipTableSourceConfig(ITableSourceConfig):
    """Marker interface for membership table source configs."""


class ActiveMembershipFilter(Filter):
    """Only display active meetings."""

    def update_query(self, query):
        return query.only_active()


class MembershipListingTab(FilteredListingTab):
    implements(IMembershipTableSourceConfig)

    filterlist_name = 'membership_state_filter'
    filterlist = FilterList(
        Filter(
            'filter_membership_all',
            _('all', default=u'All')),
        ActiveMembershipFilter(
            'filter_membership_active',
            _('active', default=u'Active'),
            default=True)
        )

    show_selects = False

    model = Membership
    sqlalchemy_sort_indexes = {'member_id': Member.fullname}
    sort_on = 'member_id'

    @property
    def columns(self):
        return (
            {'column': 'member_id',
             'column_title': _(u'column_member', default=u'Member'),
             'transform': self.get_member_link},

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
        return Membership.query.filter_by(
            committee=self.context.load_model()).join(Membership.member)

    def get_member_link(self, item, value):
        return item.member.get_link(aq_parent(aq_inner(self.context)))


@implementer(ITableSource)
@adapter(IMembershipTableSourceConfig, Interface)
class MembershipTableSource(SqlTableSource):

    searchable_columns = []
