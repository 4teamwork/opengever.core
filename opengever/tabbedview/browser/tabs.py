from DateTime import DateTime
from five import grok
from ftw.tabbedview.interfaces import ITabbedView
from ftw.table import helper
from opengever.bumblebee import get_prefered_listing_view
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.bumblebee import set_prefered_listing_view
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.dossier.interfaces import IDossierMarker
from opengever.globalindex.model.task import Task
from opengever.meeting.model.proposal import Proposal
from opengever.meeting.tabs.proposallisting import ProposalListingTab
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.tabbedview import _
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.tabbedview.browser.listing import CatalogListingView
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from opengever.tabbedview.filters import CatalogQueryFilter
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import escape_html_transform
from opengever.tabbedview.helper import external_edit_link
from opengever.tabbedview.helper import linked
from opengever.tabbedview.helper import linked_document_subdossier
from opengever.tabbedview.helper import linked_document_with_tooltip
from opengever.tabbedview.helper import linked_trashed_document_with_tooltip
from opengever.tabbedview.helper import readable_ogds_author
from opengever.tabbedview.helper import readable_ogds_user
from opengever.tabbedview.helper import workflow_state
from plone.dexterity.interfaces import IDexterityContainer
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


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


def translate_public_trial_options(item, value):
    portal = getSite()
    request = getRequest()
    return portal.translate(value, context=request, domain="opengever.base")


class DocumentsProxy(grok.View):
    """This proxyview is looking for the last used documents
    view (list or gallery) and reopens this view.
    """
    grok.name('tabbedview_view-documents-proxy')
    grok.context(ITabbedView)
    grok.require('zope2.View')

    listview = "tabbedview_view-documents"
    galleryview = "tabbedview_view-documents-gallery"

    def render(self):
        return

    def __call__(self):
        prefered_view = self.listview
        if is_bumblebee_feature_enabled():
            if get_prefered_listing_view() == 'gallery':
                prefered_view = self.galleryview

        return self.context.restrictedTraverse(prefered_view)()


class Documents(OpengeverCatalogListingTab):
    """List all documents recursively. Working copies are not listed.
    """

    grok.name('tabbedview_view-documents')

    types = ['opengever.document.document', 'ftw.mail.mail']

    columns = (

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'sortable': False,
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
         'sort_index': 'sortable_author',
         'transform': escape_html_transform},

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
         'column_title': _('label_subdossier', default="Subdossier"),
         'transform': linked_document_subdossier},

        {'column': 'public_trial',
         'column_title': _('label_public_trial', default="Public Trial"),
         'transform': translate_public_trial_options},
        )

    enabled_actions = [
        'send_as_email',
        'checkout',
        'checkin_with_comment',
        'checkin_without_comment',
        'cancel',
        'create_task',
        'submit_additional_documents',
        'trashed',
        'move_items',
        'copy_items',
        'zip_selected',
        ]

    major_actions = [
        'create_task',
        ]

    bumblebee_template = ViewPageTemplateFile('generic_with_bumblebee_viewchooser.pt')

    def __call__(self, *args, **kwargs):
        if is_bumblebee_feature_enabled():
            set_prefered_listing_view('list')
            self.template = BoundPageTemplate(self.bumblebee_template, self)

        return super(Documents, self).__call__(self, *args, **kwargs)

    @property
    def gallery_view_name(self):
        return '{}-gallery'.format(self.view_name)


class Dossiers(OpengeverCatalogListingTab):
    grok.name('tabbedview_view-dossiers')

    selection = ViewPageTemplateFile("selection_with_filters.pt")
    template = ViewPageTemplateFile("generic_with_filters.pt")

    filterlist_name = 'dossier_state_filter'
    filterlist_available = True

    filterlist = FilterList(
        Filter('filter_all', _('all')),
        CatalogQueryFilter(
            'filter_active',
            _('Active'),
            default=True,
            query_extension={'review_state': DOSSIER_STATES_OPEN})
    )

    object_provides = 'opengever.dossier.behaviors.dossier.IDossierMarker'

    columns = (

        {'column': '',
         'column_title': '',
         'transform': helper.path_checkbox,
         'sortable': False,
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


class SubDossiers(Dossiers):
    """Listing of all subdossier. Using only the base dossier tab
    configuration (without a statefilter)."""

    grok.name('tabbedview_view-subdossiers')

    search_options = {'is_subdossier': True}


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
        'export_tasks',
    ]

    major_actions = [
        'change_state',
    ]

    def get_base_query(self):
        return Task.query.by_container(self.context, get_current_admin_unit())


class Proposals(ProposalListingTab):

    grok.name('tabbedview_view-proposals')
    grok.context(IDossierMarker)

    enabled_actions = []
    major_actions = []
    sort_on = 'title'

    def get_base_query(self):
        return Proposal.query.by_container(
            self.context, get_current_admin_unit())


class Trash(Documents):
    grok.name('tabbedview_view-trash')

    types = ['opengever.dossier.dossier',
             'opengever.document.document',
             'opengever.task.task',
             'ftw.mail.mail',
             'opengever.meeting.sablontemplate', ]

    search_options = {'trashed': True}

    enabled_actions = [
        'untrashed',
        'remove',
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
