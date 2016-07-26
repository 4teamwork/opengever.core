from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact import _
from opengever.contact.interfaces import IContactFolder
from opengever.contact.models import Person
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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
             'transform': self.linked},

            {'column': 'lastname',
             'column_title': _(u'column_lastname', default=u'Lastname'),
             'transform': self.linked}
        )

    def linked(self, item, value):
        return u'<a href="{}">{}</a>'.format(item.get_url(), value)

    def get_base_query(self):
        return Person.query


class PersonTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(PersonListingTab, Interface)

    searchable_columns = [Person.firstname, Person.lastname]


class Persons(PersonListingTab):
    grok.name('tabbedview_view-persons')
    grok.context(IContactFolder)

    selection = ViewPageTemplateFile("templates/no_selection.pt")
    sort_on = 'lastname'

    enabled_actions = []
    major_actions = []
