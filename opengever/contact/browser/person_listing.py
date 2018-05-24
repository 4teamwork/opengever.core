from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact import _
from opengever.contact.models import Contact
from opengever.contact.models import Person
from opengever.tabbedview import _ as tmf
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import boolean_helper
from opengever.tabbedview.helper import linked_sql_object
from sqlalchemy.orm import joinedload
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


class IPersonTableSourceConfig(ITableSourceConfig):
    """Marker interface for person table source configs."""


class PersonListingTab(BaseListingTab):
    implements(IPersonTableSourceConfig)

    model = Person

    @property
    def columns(self):
        return (
            {'column': 'salutation',
             'column_title': _(u'column_salutation', default=u'Salutation')},

            {'column': 'academic_title',
             'column_title': _(u'column_academic_title',
                               default=u'Academic title')},

            {'column': 'firstname',
             'column_title': _(u'column_firstname', default=u'Firstname'),
             'transform': linked_sql_object},

            {'column': 'lastname',
             'column_title': _(u'column_lastname', default=u'Lastname'),
             'transform': linked_sql_object},

            {'column': 'is_active',
             'column_title': _(u'column_active', default=u'Active'),
             'transform': boolean_helper},

            {'column': 'organizations',
             'column_title': _(u'column_organizations',
                               default=u'Organizations'),
             'transform': self.organizations_links},

            {'column': 'former_contact_id',
             'column_title': _(u'column_former_contact_id',
                               default=u'Former contact id')},
        )

    def organizations_links(self, item, value):
        links = []
        for org_role in item.organizations:
            links.append(linked_sql_object(org_role.organization,
                                           org_role.organization.get_title()))

        return ', '.join(links)

    def get_base_query(self):
        return Person.query.options(joinedload('organizations'))


@implementer(ITableSource)
@adapter(IPersonTableSourceConfig, Interface)
class PersonTableSource(SqlTableSource):

    searchable_columns = [
        Person.firstname, Person.lastname, Contact.former_contact_id]


class ActiveOnlyFilter(Filter):
    def update_query(self, query):
        return query.filter_by(is_active=True)


class Persons(PersonListingTab):
    sort_on = 'lastname'

    show_selects = False
    filterlist_name = 'person_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', tmf('label_tabbedview_filter_all')),
        ActiveOnlyFilter('filter_active', tmf('Active'), default=True))

    enabled_actions = []
    major_actions = []
