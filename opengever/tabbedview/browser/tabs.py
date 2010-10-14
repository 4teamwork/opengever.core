import re
from five import grok
from Acquisition import aq_inner

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility, queryUtility, getUtilitiesFor
from zope.annotation.interfaces import IAnnotations
from plone.app.workflow.interfaces import ISharingPageRole
from plone.app.workflow.browser.sharing import SharingView

from ftw.tabbedview.browser.listing import BaseListingView
from ftw.tabbedview.interfaces import ITabbedView
from ftw.journal.interfaces import IAnnotationsJournalizable, \
    IWorkflowHistoryJournalizable, IJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.table.interfaces import ITableGenerator
from ftw.table import helper
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.helper import readable_ogds_author, linked,\
    readable_date_set_invisibles
from opengever.tabbedview import _


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

    search_options = {'isWorkingCopy': 0,
                      'trashed': False}

    columns = (
        ('', helper.draggable),
        ('', helper.path_checkbox),
        ('Title', 'sortable_title', linked),
        {'column':'document_author',
         'column_title':_('label_document_author', default="Document Author"),
         'transform': readable_ogds_author},
        {'column':'document_date',
         'column_title':_('label_document_date', default="Document Date"),
         'transform':helper.readable_date},
        {'column':'receipt_date',
         'column_title':_('label_receipt_date', default="Receipt Date"),
         'transform':helper.readable_date},
        {'column':'delivery_date',
         'column_title':_('label_delivery_date', default="Delivery Date"),
        'transform':helper.readable_date},
        {'column':'checked_out',
         'column_title':_('label_checked_out', default="Checked out by"),
        'transform':readable_ogds_author},
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
        {'column': 'reference',
         'column_title': _(u'label_reference', default=u'Reference Number')},
        ('Title', 'sortable_title', linked),
        ('review_state', 'review_state', helper.translated_string()),
        {'column':'responsible',
         'column_title':_(u'label_responsible', default=u"Responsible"),
         'transform':readable_ogds_author},
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
         'column_title': _(u'label_task_type', 'Task Type')},
        {'column': 'deadline',
         'column_title': _(u'label_deadline', 'Deadline'),
         'transform': helper.readable_date},
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
          'column_title': _('client_id', 'Client'), },
         {'column': 'sequence_number',
          'column_title': _(u'sequence_number', "Sequence Number"), },
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
        columns = ({'column': 'title',
                    'column_title': _(u'label_title', 'Title'),
                    'transform': lambda x, y: x['action']['title']},
                   {'column': 'actor',
                   'column_title': _(u'label_actor', default=u'Actor'),
                   },
                   {'column': 'time',
                    'column_title': _(u'label_time', default=u'Time'),
                    'transform': helper.readable_date_time},
                   {'column': 'comments',
                    'column_title': _(u'label_comments', default=u'Comments'),},
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
