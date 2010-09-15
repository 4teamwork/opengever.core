import re
from five import grok
from Acquisition import aq_inner

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, queryUtility, getUtilitiesFor
from zope.annotation.interfaces import IAnnotations
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow.browser.sharing import SharingView

from ftw.tabbedview.browser.listing import BaseListingView, ListingView
from ftw.tabbedview.interfaces import ITabbedView
from ftw.journal.interfaces import IAnnotationsJournalizable, \
    IWorkflowHistoryJournalizable, IJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.table.interfaces import ITableGenerator
from ftw.table import helper
from opengever.octopus.tentacle.interfaces import IContactInformation
from opengever.tabbedview.helper import readable_ogds_author, linked,\
    readable_date_set_invisibles, solr_linked
from opengever.task import _ as taskmsg


try:
    from opengever.globalsolr.interfaces import ISearch
    from collective.solr.flare import PloneFlare
except ImportError:
    pass


def datetime_compare(x, y):
    a = getattr(x, datetime_compare.index, None)
    b = getattr(y, datetime_compare.index, None)
    if a is None and b is None:
        return 0
    elif a is None:
        return -1
    elif b is None:
        return 1
    else:
        return cmp(a, b)

# #XXX really ugly. Will be overwritten in datetime_sort
datetime_compare.index = 'modified'


def custom_sort(list_, index, dir_):

    datetime_compare.index = index
    reverse = 0
    if dir_ == 'reverse':
        reverse = 1
    return sorted(list_, cmp=datetime_compare, reverse=reverse)


class OpengeverListingTab(grok.View, BaseListingView):
    grok.context(ITabbedView)
    grok.template('generic')

    update = BaseListingView.update

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('modified', helper.readable_date),
        ('Creator', readable_ogds_author),
        )


    custom_sort_indexes = {
        'Products.PluginIndexes.DateIndex.DateIndex': custom_sort}

    def _custom_sort_method(self, contents, sort_on, sort_order):

        if BaseListingView._custom_sort_method is not None:
            contents = BaseListingView._custom_sort_method(
                self, contents, sort_on, sort_order)

        if sort_on=='reference':
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
            contents = list(contents)
            contents.sort(
                lambda a, b: cmp(_sortable_data(a), _sortable_data(b)))
            if sort_order!='asc':
                contents.reverse()

        elif sort_on in ('responsible',
            'Creator', 'checked_out', 'issuer', 'contact'):
            info = getUtility(IContactInformation)

            def _sorter(a, b):
                av = (info.describe(getattr(a, sort_on, '')) or '').lower()
                bv = (info.describe(getattr(b, sort_on, '')) or '').lower()
                return cmp(av, bv)

            contents = list(contents)
            contents.sort(_sorter)
            if sort_order!='asc':
                contents.reverse()
        return contents

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]

    #only 'SearchableText' is implemented for now
    search_index = 'SearchableText'
    sort_on = 'modified'
    sort_order = 'reverse'


class SolrListingView(ListingView):

    sort_on = ''

    def build_query(self):
        return self.search_util.buildQuery(**self._search_options)

    def update(self):
        self.search_util = queryUtility(ISearch)

        if not 'portal_type' in self.search_options and len(self.types):
            self.search_options.update({'portal_type': self.types[0]})

        self.search()

    def search(self, kwargs={}):

        parameters = {}
        self.sort_on = self.request.get('sort_on', self.sort_on)
        self.sort_order = self.request.get('sort_order', self.sort_order)

        parameters['sort'] = self.sort_on
        if self.sort_on:
            if self.sort_on.startswith('header-'):
                self.sort_on = self.sort_on.split('header-')[1]
                parameters['sort'] = self.sort_on

            if self.sort_order == 'reverse':
                parameters['sort'] = '%s desc' % parameters['sort']
            else:
                parameters['sort'] = '%s asc' % parameters['sort']

        query = self.build_query()
        flares = self.search_util(query, **parameters)
        self.contents = [PloneFlare(f) for f in flares]


class OpengeverSolrListingTab(grok.View, SolrListingView):
    grok.context(ITabbedView)
    grok.template('generic')

    update = SolrListingView.update

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', solr_linked),
        ('modified', helper.readable_date),
        ('Creator', readable_ogds_author),
        )

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class OpengeverTab(object):
    show_searchform = False

    def get_css_classes(self):
        if self.show_searchform:
            return ['searchform-visible']
        else:
            return ['searchform-hidden']


class Documents(OpengeverListingTab):
    grok.name('tabbedview_view-documents')

    types = ['opengever.document.document', 'ftw.mail.mail']

    search_options = {'isWorkingCopy': 0}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        ('document_author', 'document_author'),
        ('document_date', 'document_date', helper.readable_date),
        ('receipt_date', 'receipt_date', helper.readable_date),
        ('delivery_date', 'delivery_date', helper.readable_date),
        ('checked_out', 'checked_out', readable_ogds_author),
        )

    enabled_actions = ['cut',
                       'copy',
                       'paste',
                       'send_as_email',
                       'checkout',
                       'checkin',
                       'cancel',
                       'create_task',
                       'trashed',
                       'send_documents',
                       'copy_documents_to_remote_client',
                       ]

    major_actions = ['send_documents',
                     'checkout',
                     'checkin',
                     'create_task',
                     ]


class Dossiers(OpengeverListingTab):

    grok.name('tabbedview_view-dossiers')

    types = [
        'opengever.dossier.projectdossier',
        'opengever.dossier.businesscasedossier',
        ]

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('reference'),
        ('Title', 'sortable_title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        ('responsible', readable_ogds_author),
        ('start', helper.readable_date),
        ('end', helper.readable_date),

        )

    search_options = {'is_subdossier': False}

    enabled_actions = ['change_state',
                       'cut',
                       'copy',
                       'paste',
                       ]

    major_actions = ['change_state',
                     ]


class SubDossiers(Dossiers):

    grok.name('tabbedview_view-subdossiers')
    search_options = {'is_subdossier': True}


class Tasks(OpengeverListingTab):

    grok.name('tabbedview_view-tasks')

    columns= (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('review_state', 'review_state', helper.translated_string()),
        ('Title', 'sortable_title', linked),
        {'column': 'task_type',
         'column_title': taskmsg(u'label_task_type', 'Task Type')},
        ('deadline', helper.readable_date),
        ('date_of_completion', readable_date_set_invisibles), # erledigt am
        {'column': 'responsible',
         'column_title': taskmsg(u'label_responsible_task', 'Responsible'),
         'transform': readable_ogds_author},
        ('issuer', readable_ogds_author), # zugewiesen von
        {'column': 'created',
         'column_title': taskmsg(u'label_issued_date', 'issued at'),
         'transform': helper.readable_date},
         {'column': 'client_id',
          'column_title': taskmsg('client_id', 'Client'), },
         {'column': 'sequence_number',
          'column_title': taskmsg(u'sequence_number', "Sequence Number"), },
        )

    types = ['opengever.task.task', ]

    enabled_actions = [
        'change_state',
        'cut',
        'paste',
        ]


class Events(OpengeverListingTab):
    grok.name('tabbedview_view-events')

    types = ['dummy.event', ]


class Journal(grok.View, OpengeverTab):

    grok.context(IJournalizable)
    grok.name('tabbedview_view-journal')
    grok.template('journal')

    def table(self):
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        columns = (('title', lambda x, y: x['action']['title']),
                   'actor',
                   ('time', helper.readable_date_time),
                   'comments',
                   )
        return generator.generate(
            reversed(self.data()),
                columns, css_mapping={'table': 'journal-listing'})

    def data(self):
        context = self.context
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(context)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented


class Trash(OpengeverListingTab):
    grok.name('tabbedview_view-trash')

    types = ['opengever.dossier.dossier',
             'opengever.document.document',
             'opengever.task.task',
             'ftw.mail.mail', ]

    search_options = {'trashed': True}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        )

    enabled_actions = ['untrashed', ]


class Sharing(SharingView):

    template = ViewPageTemplateFile('tabs_templates/sharing.pt')

    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

        - id
        - title
        """
        context = aq_inner(self.context)
        pairs = []
        has_manage_portal = context.portal_membership.checkPermission(
            'ManagePortal', context)
        aviable_roles_for_users = [
            u'Editor', u'Reader', u'Contributor', u'Reviewer', ]
        for name, utility in getUtilitiesFor(ISharingPageRole):
            if not has_manage_portal and name not in aviable_roles_for_users:
                continue
            pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs

    def role_settings(self):

        context = self.context
        results = super(Sharing, self).role_settings()

        if not context.portal_membership.checkPermission(
            'ManagePortal', context):
            results = [r for r in results if r['type']!='group']

        return results
