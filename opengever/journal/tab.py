from copy import deepcopy
from five import grok
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.journal.interfaces import IJournalizable
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from opengever.tabbedview.browser.listing import ListingView
from ftw.table import helper
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig, ITableSource
from opengever.journal import _
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import linked_ogds_author
from zope.annotation.interfaces import IAnnotations
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface import implements, Interface
from zope.i18n import translate
from zope.globalrequest import getRequest
from BeautifulSoup import BeautifulSoup

def tooltip_helper(item, value):
    text = ''.join(BeautifulSoup(value).findAll(text=True))
    return '<span title="%s">%s</span>' % (text.encode('utf-8'), value)


def title_helper(item, value):
    return translate(item['action'].get('title'),
                    context=getRequest())


class IJournalSourceConfig(ITableSourceConfig):
    """Marker interface for journal table source config.
    """


class JournalTab(grok.View, OpengeverTab, ListingView):
    """Journal tab implementing IJorunalConfig.
    """

    implements(IJournalSourceConfig)

    grok.name('tabbedview_view-journal')
    grok.require('zope2.View')
    grok.context(IJournalizable)

    # do not select
    select_all_template = lambda *a, **kw: ''

    sort_on = 'time'
    sort_reverse = True

    # do not show the selects, because no action is enabled
    show_selects = False
    enabled_actions = [
        'reset_tableconfiguration',
        ]
    major_actions = []
    selection = ViewPageTemplateFile("no_selection_amount.pt")

    columns = (
        {'column': 'title',
         'column_title': _(u'label_title', 'Title'),
         'transform': title_helper},

        {'column': 'actor',
         'column_title': _(u'label_actor', default=u'Actor'),
         'transform': linked_ogds_author},

        {'column': 'time',
         'column_title': _(u'label_time', default=u'Time'),
         'transform': helper.readable_date_time},

        {'column': 'comments',
         'column_title': _(u'label_comments', default=u'Comments'),
         'transform': tooltip_helper},
        )

    def get_base_query(self):
        return None

    __call__ = ListingView.__call__
    update = ListingView.update
    render = __call__


class JournalTableSource(grok.MultiAdapter, BaseTableSource):

    grok.implements(ITableSource)
    grok.adapts(IJournalSourceConfig, Interface)

    def validate_base_query(self, query):
        context = self.config.context
        if IAnnotationsJournalizable.providedBy(context):
            annotations = IAnnotations(context)
            data = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(context):
            raise NotImplemented

        data = deepcopy(data)
        return data

    def extend_query_with_ordering(self, results):
        if self.config.sort_on:
            sorter = lambda a, b: cmp(getattr(a, self.config.sort_on, ''),
                                      getattr(b, self.config.sort_on, ''))
            results.sort(sorter)

        if self.config.sort_on and self.config.sort_reverse:
            results.reverse()

        return results

    def extend_query_with_textfilter(self, results, text):
        if not len(text):
            return results

        if text.endswith('*'):
            text = text[:-1]

        def _search_method(item):
            # title
            if text.lower() in title_helper(item, '').lower():
                return True

            # actor
            if text.lower() in item.get('actor', ''):
                return True

            # comment
            if text.lower() in item.get('comment', ''):
                return True

            return False

        results = filter(_search_method, results)

        return results

    def search_results(self, results):
        return results
