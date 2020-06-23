from ftw.table import helper
from ftw.table.interfaces import ITableSource
from opengever.base import ISearchSettings
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview import GeverCatalogTableSource
from opengever.tabbedview.helper import linked
from opengever.tabbedview.interfaces import IGeverCatalogTableSourceConfig
from opengever.task import _ as taskmsg
from opengever.task.helper import task_type_helper
from opengever.tasktemplates import _
from opengever.tasktemplates.browser.helper import interactive_user_helper
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from plone import api
from plone.dexterity.browser.view import DefaultView
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component._api import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface


def preselected_helper(item, value):
    if value is True:
        return translate(
            _(u'preselected_yes', default=u'Yes'),
            context=getSite().REQUEST)
    else:
        return ''


class ITaskTemplatesCatalogTableSourceConfig(IGeverCatalogTableSourceConfig):
    pass


@implementer(ITableSource)
@adapter(ITaskTemplatesCatalogTableSourceConfig, Interface)
class TaskTemplatesCatalogTableSource(GeverCatalogTableSource):

    def search_results(self, query):
        # Backup the sort on parameter because it will be gone after the call
        # to the super class.
        sort_on = query.get('sort_on')

        search_results = super(TaskTemplatesCatalogTableSource, self).search_results(query)

        # Manually sort the Solr search results by their position in the parent
        # because Solr does not support `getObjPositionInParent` for sorting.
        if self.use_solr and sort_on == 'getObjPositionInParent':
            parent = api.content.get(query['path']['query'])
            search_results.docs = sorted(
                search_results.docs,
                key=lambda doc: parent.objectIds().index(doc['id'])
            )

        return search_results


class TaskTemplates(BaseCatalogListingTab):

    implements(ITaskTemplatesCatalogTableSourceConfig)

    columns = (
        {'column': '',
         'column_title': '',
         'transform': helper.draggable,
         'sortable': False,
         'width': 30},

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'sortable': False,
         'groupable': False,
         'width': 30},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'sortable': False,
         'transform': linked},

        {'column': 'task_type',
         'column_title': taskmsg(u'label_task_type', 'Task Type'),
         'sortable': False,
         'transform': task_type_helper},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', 'Issuer'),
         'sortable': False,
         'transform': interactive_user_helper},

        {'column': 'responsible',
         'column_title': _(u'label_responsible_task', default=u'Responsible'),
         'sortable': False,
         'transform': interactive_user_helper},

        {'column': 'period',
         'sortable': False,
         'column_title': _(u"label_deadline", default=u"Deadline in Days")},

        {'column': 'preselected',
         'column_title': _(u"label_preselected", default=u"Preselect"),
         'sortable': False,
         'transform': preselected_helper},
        )

    sort_on = 'draggable'

    types = ['opengever.tasktemplates.tasktemplate', ]

    enabled_actions = ['folder_delete_confirmation']

    major_actions = ['folder_delete_confirmation']


class View(DefaultView):

    def comments(self):
        text = ITaskTemplate(self.context).text
        if text:
            transformer = api.portal.get_tool(name='portal_transforms')
            converted = transformer.convertTo(
                'text/html', safe_unicode(text), mimetype='text/x-web-intelligent')
            return converted.getData()

    def responsible_link(self):
        task = ITaskTemplate(self.context)
        return interactive_user_helper(task, task.responsible)

    def issuer_link(self):
        task = ITaskTemplate(self.context)
        return interactive_user_helper(task, task.issuer)
