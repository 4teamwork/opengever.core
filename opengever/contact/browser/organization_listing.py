from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact import _
from opengever.contact.interfaces import IContactFolder
from opengever.contact.models import Organization
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import SqlTableSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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
             'transform': self.linked},
        )

    def linked(self, item, value):
        return u'<a href="{}">{}</a>'.format(item.get_url(), value)

    def get_base_query(self):
        return Organization.query


class OrganizationTableSource(SqlTableSource):
    grok.implements(ITableSource)
    grok.adapts(OrganizationListingTab, Interface)

    searchable_columns = [Organization.name]


class Organizations(OrganizationListingTab):
    grok.name('tabbedview_view-organizations')
    grok.context(IContactFolder)

    selection = ViewPageTemplateFile("templates/no_selection.pt")
    sort_on = 'name'

    enabled_actions = []
    major_actions = []
