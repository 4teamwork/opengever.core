from five import grok
from ftw.tabbedview.interfaces import ITabbedView
from ftw.table import helper
from ftw.table.catalog_source import CatalogTableSource
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.interfaces import IDossierMarker
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import CatalogListingView
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from opengever.tabbedview.helper import external_edit_link
from opengever.tabbedview.helper import linked_document_with_tooltip
from opengever.tabbedview.helper import linked_trashed_document_with_tooltip
from opengever.tabbedview.helper import readable_ogds_author, linked
from opengever.tabbedview.helper import readable_ogds_user
from opengever.tabbedview.helper import workflow_state
from opengever.tabbedview.interfaces import IStateFilterTableSourceConfig
from plone.dexterity.interfaces import IDexterityContainer
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class OpengeverCatalogListingTab(grok.View, OpengeverTab, CatalogListingView):
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

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'width': 30},

        {'column': 'sequence_number',
         'column_title': _(u'document_sequence_number',
                           default=u'Sequence Number'),
         'sort_index': 'sequence_number'},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked_document_with_tooltip},

        {'column': 'document_author',
         'column_title': _('label_document_author', default="Document Author"),
         'sort_index': 'sortable_author'},

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

        )

    enabled_actions = [
        'send_as_email',
        'checkout',
        'checkin',
        'cancel',
        'create_task',
        'trashed',
        'move_items',
        'copy_items',
        'zip_selected',
        ]

    major_actions = [
        'create_task',
        ]


class BaseDossiersTab(OpengeverCatalogListingTab):

    object_provides = 'opengever.dossier.behaviors.dossier.IDossierMarker'

    columns = (

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'width': 30},

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
        )

    search_options = {'is_subdossier': False}

    enabled_actions = ['change_state',
                       'pdf_dossierlisting',
                       'export_dossiers',
                       'move_items',
                       'copy_items',
                       ]

    major_actions = ['change_state', ]


class Dossiers(BaseDossiersTab):
    """Dossier listing view. Using the base dossier tab configuration
    and install additonaly a statefilter (active/all)."""

    grok.name('tabbedview_view-dossiers')

    implements(IStateFilterTableSourceConfig)

    selection = ViewPageTemplateFile("selection_dossier.pt")

    template = ViewPageTemplateFile("generic_dossier.pt")

    open_states = DOSSIER_STATES_OPEN

    state_filter_name = 'dossier_state_filter'


class SubDossiers(BaseDossiersTab):
    """Listing of all subdossier. Using only the base dossier tab
    configuration (without a statefilter)."""

    grok.name('tabbedview_view-subdossiers')
    search_options = {'is_subdossier': True}


class StateFilterTableSource(grok.MultiAdapter, CatalogTableSource):
    """Catalog Table source Adapter,
    which provides open/all state filtering."""

    adapts(IStateFilterTableSourceConfig, Interface)

    def build_query(self):
        """extends the standard catalog soruce build_query with the
        extend_query_with_statefilter functionality.
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
        review_state_filter = self.request.get(
            self.config.state_filter_name, None)

        # when state_filter is not set to all, we just return the open states
        if review_state_filter != 'false':
            query = self.extend_query_with_statefilter(query)

        # batching
        if self.config.batching_enabled and not self.config.lazy:
            query = self.extend_query_with_batching(query)

        return query

    def extend_query_with_statefilter(self, query):
        """Extends the given query with a filter,
        which show just objects in the open state."""

        query['review_state'] = self.config.open_states
        return query


class Tasks(GlobalTaskListingTab):

    grok.name('tabbedview_view-tasks')
    grok.context(IDossierMarker)

    columns = GlobalTaskListingTab.columns + (
        {'column': 'containing_subdossier',
         'column_title': _('label_subdossier', default="Subdossier"), },
    )

    enabled_actions = [
        'change_state',
        'pdf_taskslisting',
        'move_items',
        'copy_items',
        'export_tasks',
    ]

    major_actions = [
        'change_state',
    ]

    def get_base_query(self):
        return Task.query.by_container(self.context, get_current_admin_unit())


class Trash(Documents):
    grok.name('tabbedview_view-trash')

    types = ['opengever.dossier.dossier',
             'opengever.document.document',
             'opengever.task.task',
             'ftw.mail.mail', ]

    search_options = {'trashed': True}

    enabled_actions = [
        'untrashed',
        ]

    major_actions = []

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
        and remove some columns and adjust some helper methods.
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
                # append column
                columns.append(col.copy())

                # change helper method for the title column
                if col.get('column') == 'Title':
                    columns[-1][
                        'transform'] = linked_trashed_document_with_tooltip
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
