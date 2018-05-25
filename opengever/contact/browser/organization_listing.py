from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact import _
from opengever.contact.browser.person_listing import ActiveOnlyFilter
from opengever.contact.models import Contact
from opengever.contact.models import Organization
from opengever.tabbedview import _ as tmf
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import boolean_helper
from opengever.tabbedview.helper import linked_sql_object
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IOrganizationTableSourceConfig(ITableSourceConfig):
    """Marker interface for organization table source configs."""


class OrganizationListingTab(BaseListingTab):
    implements(IOrganizationTableSourceConfig)

    model = Organization

    @property
    def columns(self):
        return (
            {'column': 'name',
             'column_title': _(u'column_name', default=u'Name'),
             'transform': linked_sql_object},

            {'column': 'is_active',
             'column_title': _(u'column_active', default=u'Active'),
             'transform': boolean_helper},

            {'column': 'former_contact_id',
             'column_title': _(u'column_former_contact_id',
                               default=u'Former contact id')},

        )

    def get_base_query(self):
        return Organization.query


@implementer(ITableSource)
@adapter(IOrganizationTableSourceConfig, Interface)
class OrganizationTableSource(SqlTableSource):

    searchable_columns = [Organization.name, Contact.former_contact_id]


class Organizations(OrganizationListingTab):
    sort_on = 'name'

    show_selects = False
    filterlist_name = 'organization_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', tmf('label_tabbedview_filter_all')),
        ActiveOnlyFilter('filter_active', tmf('Active'), default=True))

    enabled_actions = []
    major_actions = []
