from ftw.table.helper import path_checkbox
from opengever.disposition import _
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.filters import CatalogQueryFilter
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.helper import linked
from opengever.tabbedview.helper import workflow_state


ACTIVE_STATES = ['disposition-state-in-progress',
                 'disposition-state-appraised',
                 'disposition-state-disposed',
                 'disposition-state-archived']


class Dispositions(BaseCatalogListingTab):

    types = ['opengever.disposition.disposition']
    enabled_actions = []
    major_actions = []

    filterlist_name = 'disposition_state_filter'
    filterlist_available = True
    filterlist = FilterList(
        Filter('filter_all', _('all')),
        CatalogQueryFilter(
            'filter_active', _('active'), default=True,
            query_extension={'review_state': ACTIVE_STATES})
    )

    columns = (

        {'column': '',
         'column_title': '',
         'transform': path_checkbox,
         'sortable': False,
         'width': 30},

        {'column': 'sequence_number',
         'column_title': _(u'document_sequence_number',
                           default=u'Sequence Number'),
         'sort_index': 'sequence_number'},

        {'column': 'Title',
         'column_title': _(u'label_title', default=u'Title'),
         'sort_index': 'sortable_title',
         'transform': linked},

        {'column': 'review_state',
         'column_title': _(u'label_review_state', default=u'Review state'),
         'transform': workflow_state},
    )
