from five import grok
from ftw.table.helper import path_checkbox
from opengever.disposition import _
from opengever.tabbedview import BaseCatalogListingTab
from opengever.tabbedview.helper import linked


class Dispositions(BaseCatalogListingTab):
    grok.name('tabbedview_view-dispositions')

    types = ['opengever.disposition.disposition']
    enabled_actions = []
    major_actions = []

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
    )
