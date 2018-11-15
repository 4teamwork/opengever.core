from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from ftw.table import helper
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.contact.utils import get_contactfolder_url
from opengever.journal import _
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import GeverTableSource
from opengever.tabbedview.helper import linked_ogds_author
from opengever.tabbedview.helper import readable_ogds_user
from opengever.tabbedview.helper import tooltip_helper
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Interface
import cPickle


def title_helper(*args):
    """Translate item action titles. All values we'd ever get are empty."""
    return translate(args[0]['action']['title'], context=getRequest())


class IJournalSourceConfig(ITableSourceConfig):
    """Marker interface for journal table source config."""


class JournalTab(BaseListingTab):
    """Journal tab implementing IJorunalConfig."""

    implements(IJournalSourceConfig)

    reference_template = ViewPageTemplateFile('templates/journal_references.pt')

    sort_on = 'time'
    sort_reverse = True

    # do not show the selects, because no action is enabled
    show_selects = False
    enabled_actions = []
    major_actions = []
    selection = ViewPageTemplateFile("templates/journal_selection.pt")

    def __init__(self, context, request):
        super(JournalTab, self).__init__(context, request)
        self.documents = []
        self.contacts = []
        self.users = []

    @property
    def columns(self):
        return (
            {'column': 'time', 'column_title': _(u'label_time', default=u'Time'), 'transform': helper.readable_date_time},
            {'column': 'title', 'column_title': _(u'label_title', 'Title'), 'transform': title_helper},
            {'column': 'actor', 'column_title': _(u'label_actor', default=u'Changed by'), 'transform': linked_ogds_author},
            {'column': 'comments', 'column_title': _(u'label_comments', default=u'Comments'), 'transform': tooltip_helper, 'sortable': False},  # noqa: E501
            {'column': 'references', 'column_title': _(u'label_references', default=u'References'), 'transform': self.journal_references, 'sortable': False},  # noqa: E501
        )

    def journal_references(self, *args):
        item = args[0]
        self.documents = item.get('action').get('documents', [])
        self.contacts = item.get('action').get('contacts', [])
        self.users = item.get('action').get('users', [])
        return self.reference_template(self)

    @staticmethod
    def get_contactfolder_url():
        return get_contactfolder_url()

    def get_base_query(self):
        return None

    def manual_entry_allowed(self):
        return api.user.has_permission('Modify portal content', user=api.user.get_current(), obj=self.context)


def time_column_sorter(a, b):
    """Sort by timestamp."""
    return cmp(a.get('time', ''), b.get('time', ''))


def title_column_sorter(a, b):
    """Sort by title."""
    return cmp(a.get('action', {}).get('title'), b.get('action', {}).get('title'))


def actor_column_sorter(a, b):
    """Sort by user label (`lastname firstname (userid)`)."""
    return cmp(readable_ogds_user(a, a.get('actor')), readable_ogds_user(b, b.get('actor')))


@implementer(ITableSource)
@adapter(IJournalSourceConfig, Interface)
class JournalTableSource(GeverTableSource):
    """Generate a table to display in the journal tab view."""

    sorter = {
        'actor': actor_column_sorter,
        'time': time_column_sorter,
        'title': title_column_sorter,
    }

    batching_enabled = True

    def validate_base_query(self, query):
        context = self.config.context
        if IAnnotationsJournalizable.providedBy(context):
            annotations = IAnnotations(context)
            data = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(context):
            raise NotImplementedError

        # XXX - a performance hack to replace deepcopy(data)
        # This only works as persistent objects are guaranteed to be picklable
        data = cPickle.loads(cPickle.dumps(data))
        return data

    def extend_query_with_ordering(self, results):
        if self.config.sort_on:
            sorter = self.sorter.get(self.config.sort_on)
            results.sort(sorter)

        if self.config.sort_on and self.config.sort_reverse:
            results.reverse()

        return results

    def extend_query_with_textfilter(self, results, text):
        if not text:
            return results

        if text.endswith('*'):
            text = text[:-1]

        def _search_method(item):
            # title
            if text.lower() in title_helper(item, u'').lower().encode('utf-8'):
                return True

            # actor
            if text.lower() in item.get('actor', '').lower():
                return True

            # comment
            if text.lower() in item.get('comments', '').lower():
                return True

            return False

        results = filter(_search_method, results)

        return results

    def search_results(self, results):
        return results
