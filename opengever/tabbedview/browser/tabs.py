from five import grok
from ftw.dictstorage.interfaces import ISQLAlchemy
from ftw.tabbedview.interfaces import ITabbedView
from ftw.table import helper
from ftw.table.catalog_source import CatalogTableSource
from opengever.base.browser.helper import client_title_helper
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview import _
from opengever.tabbedview.browser.listing import CatalogListingView
from opengever.tabbedview.helper import display_client_title_condition
from opengever.tabbedview.helper import external_edit_link
from opengever.tabbedview.helper import overdue_date_helper
from opengever.tabbedview.helper import readable_date_set_invisibles
from opengever.tabbedview.helper import readable_ogds_author, linked
from opengever.tabbedview.helper import readable_ogds_user
from opengever.tabbedview.helper import workflow_state
from opengever.tabbedview.interfaces import ITaskCatalogTableSourceConfig
from opengever.task.helper import task_type_helper
from plone.dexterity.interfaces import IDexterityContainer
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility, adapts
from zope.interface import Interface
from zope.interface import implements
import re


class OpengeverTab(object):
    implements(ISQLAlchemy)

    show_searchform = True

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']

    # XXX : will be moved to registry later...
    extjs_enabled = True

    def custom_sort(self, results, sort_on, sort_reverse):
        """We need to handle some sorting for special columns, which are
        not sortable in the catalog...
        """

        if getattr(self, '_custom_sort_method', None) is not None:
            results = self._custom_sort_method(results, sort_on, sort_reverse)

        elif sort_on == 'reference' or sort_on == 'sequence_number':
            splitter = re.compile('[/\., ]')

            def _sortable_data(brain):
                """ Converts the "reference" into a tuple containing integers,
                which are converted well. Sorting "10" and "2" as strings
                results in wrong order..
                """

                value = getattr(brain, sort_on, '')
                if not isinstance(value, str) and not isinstance(
                    value, unicode):
                    return value
                parts = []
                for part in splitter.split(value):
                    part = part.strip()
                    try:
                        part = int(part)
                    except ValueError:
                        pass
                    parts.append(part)
                return parts
            results = list(results)
            results.sort(
                lambda a, b: cmp(_sortable_data(a), _sortable_data(b)))
            if sort_reverse:
                results.reverse()

        #custom sort for sorting on the readable fullname of the users, contacts and inboxes
        elif sort_on in ('responsible','Creator', 'checked_out', 'issuer', 'contact'):
            info = getUtility(IContactInformation)

            if sort_on in ('issuer', 'contact'):
                sort_dict = info.get_user_contact_sort_dict()
            else:
                sort_dict = info.get_user_sort_dict()

            def _sorter(a, b):
                return cmp(
                    sort_dict.get(getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    sort_dict.get(getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            def _reverse_sorter(b, a):
                return cmp(
                    sort_dict.get(getattr(a, sort_on, ''), getattr(a, sort_on, '')),
                    sort_dict.get(getattr(b, sort_on, ''), getattr(b, sort_on, ''))
                    )

            results = list(results)

            if sort_reverse:
                results.sort(_reverse_sorter)
            else:
                results.sort(_sorter)
        return results


class OpengeverCatalogListingTab(grok.View, OpengeverTab,
                                 CatalogListingView):
    """Base view for catalog listing tabs.
    """

    grok.context(ITabbedView)
    grok.require('zope2.View')

    columns = ()

    search_index = 'SearchableText'
    sort_on = 'modified'
    sort_order = 'reverse'

    __call__ = CatalogListingView.__call__
    update = CatalogListingView.update
    render = __call__


class Documents(OpengeverCatalogListingTab):
    """List all documents recursively. Working copies are not listed.
    """

    grok.name('tabbedview_view-documents')

    types = ['opengever.document.document', 'ftw.mail.mail']

    columns = (

        ('', helper.path_checkbox),

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},

        {'column': 'document_author',
         'column_title': _('label_document_author', default="Document Author"),
         'sort_index': 'sortable_author',
         'transform': readable_ogds_author},

        {'column': 'document_date',
         'column_title': _('label_document_date', default="Document Date"),
         'transform': helper.readable_date},

        {'column': 'receipt_date',
         'column_title': _('label_receipt_date', default="Receipt Date"),
         'transform': helper.readable_date},

        {'column': 'delivery_date',
         'column_title': _('label_delivery_date', default="Delivery Date"),
         'transform': helper.readable_date},

        {'column': 'checked_out',
         'column_title': _('label_checked_out', default="Checked out by"),
         'transform': readable_ogds_user},

        {'column': 'containing_subdossier',
         'column_title': _('label_subdossier', default="Subdossier"), },

        ('', external_edit_link),

        )

    enabled_actions = [
                       'send_as_email',
                       'checkout',
                       'checkin',
                       'cancel',
                       'create_task',
                       'trashed',
                       'send_documents',
                       'move_items',
                       'copy_items',
                       'reset_tableconfiguration',
                       ]

    major_actions = ['send_documents',
                     'create_task',
                     ]


class Dossiers(OpengeverCatalogListingTab):

    grok.name('tabbedview_view-dossiers')

    object_provides = 'opengever.dossier.behaviors.dossier.IDossierMarker'


    columns = (
        ('', helper.path_checkbox),

        {'column': 'reference',
         'column_title': _(u'label_reference', default=u'Reference Number')},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},

        {'column': 'review_state',
         'column_title': _(u'label_review_state', default=u'Review state'),
         'transform': workflow_state},

        {'column': 'responsible',
         'column_title': _(u'label_dossier_responsible',
                          default=u"Responsible"),
         'transform': readable_ogds_author},

        {'column': 'start',
         'column_title': _(u'label_start', default=u'Start'),
         'transform': helper.readable_date},

        {'column': 'end',
         'column_title': _(u'label_end', default=u'End'),
         'transform': helper.readable_date},
        {'column': 'filing_no',
         'column_title': _(u'filing_number', default=u'Filing Number')},
        )

    search_options = {'is_subdossier': False}

    enabled_actions = ['change_state',
                       'pdf_dossierlisting',
                       'export_dossiers',
                       'move_items',
                       'copy_items',
                       'reset_tableconfiguration',
                       ]

    major_actions = ['change_state',
                     ]


class SubDossiers(Dossiers):

    grok.name('tabbedview_view-subdossiers')
    search_options = {'is_subdossier': True}


class TaskCatalogTableSource(grok.MultiAdapter, CatalogTableSource):
    """Table source Adapter for task stored in the portal catalog"""

    adapts(ITaskCatalogTableSourceConfig, Interface)

    def build_query(self):
        """extends the standard catalog soruce build_query with the
        extend_query_with_taskstatefilter functionality.
        """

        # initalize config
        self.config.update_config()

        # get the base query from the config
        query = self.config.get_base_query()
        query = self.validate_base_query(query)

        # ordering
        query = self.extend_query_with_ordering(query)

        # filter
        if self.config.filter_text:
            query = self.extend_query_with_textfilter(
                query, self.config.filter_text)

        # reviewstate-filter
        review_state_filter = self.request.get('review_state', None)

        # when state_filter is not set to all, we just return the open states
        if review_state_filter != 'false':
            query = self.extend_query_with_taskstatefilter(query)

        # batching
        if self.config.batching_enabled and not self.config.lazy:
            query = self.extend_query_with_batching(query)

        return query

    def extend_query_with_taskstatefilter(self, query):
        """Extends the given query with a filter,
        which show just open dossiers."""

        open_task_states = [
            'task-state-open',
            'task-state-in-progress',
            'task-state-resolved',
            'task-state-rejected',
            'forwarding-state-open',
        ]

        query['review_state'] = open_task_states

        return query


class Tasks(OpengeverCatalogListingTab):

    implements(ITaskCatalogTableSourceConfig)

    grok.name('tabbedview_view-tasks')

    template = ViewPageTemplateFile("generic_task.pt")

    selection = ViewPageTemplateFile("selection_tasks.pt")

    columns = (
        ('', helper.path_checkbox),

        {'column': 'review_state',
         'column_title': _(u'label_review_state', default=u'Review state'),
         'transform': workflow_state},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},

        {'column': 'task_type',
         'column_title': _(u'label_task_type', 'Task Type'),
         'transform': task_type_helper},

        {'column': 'deadline',
         'column_title': _(u'label_deadline', 'Deadline'),
         'transform': overdue_date_helper},

        {'column': 'date_of_completion',
         'column_title': _(u'label_date_of_completion', 'Date of Completion'),
         'transform': readable_date_set_invisibles},

        {'column': 'responsible',
         'column_title': _(u'label_responsible_task', 'Responsible'),
         'transform': readable_ogds_author},

        {'column': 'issuer',
         'column_title': _(u'label_issuer', 'Issuer'),
         'transform': readable_ogds_author},

        {'column': 'created',
         'column_title': _(u'label_issued_date', 'issued at'),
         'transform': helper.readable_date},

        {'column': 'client_id',
         'column_title': _('client_id', 'Client'),
         'transform': client_title_helper,
         'condition': display_client_title_condition},

        {'column': 'sequence_number',
         'column_title': _(u'sequence_number', "Sequence Number"), },

        {'column': 'containing_subdossier',
         'column_title': _('label_subdossier', default="Subdossier"), },
        )

    types = ['opengever.task.task', ]

    enabled_actions = [
        'change_state',
        'pdf_taskslisting',
        'move_items',
        'copy_items',
        'export_dossiers',
        'reset_tableconfiguration',
        ]

    major_actions = ['change_state',
                     ]


class Trash(Documents):
    grok.name('tabbedview_view-trash')

    types = ['opengever.dossier.dossier',
             'opengever.document.document',
             'opengever.task.task',
             'ftw.mail.mail', ]

    search_options = {'trashed': True}

    enabled_actions = [
        'untrashed',
        'reset_tableconfiguration',]

    major_actions= [
        'reset_tableconfiguration',
        ]

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
           remove some columns from the columns property
        """
        remove_columns = ['checked_out', ]
        columns = []
        for col in super(Trash, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass  # remove this column
            elif isinstance(col, tuple) and \
                    col[1] == external_edit_link:
                pass  # remove external_edit colunmn
            else:
                columns.append(col)

        return columns


class DocumentRedirector(grok.View):
    """Redirector View is called after a Document is created,
    make it easier to implement type specifics immediate_views
    like implemented for opengever.task"""

    grok.name('document-redirector')
    grok.context(IDexterityContainer)
    grok.require('cmf.AddPortalContent')

    def render(self):
        referer = self.context.REQUEST.environ.get('HTTP_REFERER')
        if referer.endswith('++add++opengever.document.document'):
            return self.context.REQUEST.RESPONSE.redirect(
                '%s#documents' % self.context.absolute_url())

        return self.context.REQUEST.RESPONSE.redirect(
            self.context.absolute_url())
