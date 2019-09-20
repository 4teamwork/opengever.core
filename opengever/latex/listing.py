from collections import OrderedDict
from ftw.table import helper
from opengever.activity import _ as activity_mf
from opengever.journal import _ as journal_mf
from opengever.journal.handlers import DOCUMENT_SENT
from opengever.journal.tab import title_helper
from opengever.latex import _
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import get_responsible_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.repository.interfaces import IRepositoryFolder
from opengever.task.helper import task_type_helper
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class Column(object):

    def __init__(self, id, label, width, getter=None, alignment=None):
        self.id = id
        self.label = label
        self.width = width
        self.alignment = alignment or "justify"

        if getter is None:
            getter = id

        if isinstance(getter, basestring):
            self.getter = lambda item: getattr(item, getter)
        else:
            self.getter = getter

    def get_value(self, item):
        value = self.getter(item)
        if value is None:
            value = u''

        return value

    def get_width(self):
        if not self.width.endswith("%"):
            raise NotImplementedError("Only implemented for width in percentage")
        return float(self.width.split("%")[0])


class ILaTexListing(Interface):

    def get_labels():
        """"Returns a LaTEx string with the labels of the listing"""

    def get_widths():
        """"Returns a LaTEx string with the widths of the listing,
        which are calculated."""

    def get_rows():
        """"Returns a LaTEx string with all the rows of the listing"""

    def get_config():
        """Returns the table configuration, a list of dicts for every row,
        containing label, width, getter."""


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class LaTexListing(object):

    template = ViewPageTemplateFile('templates/listing.pt')

    def __init__(self, context, request, latex_view):
        self.context = context
        self.request = request
        self.latex_view = latex_view

        self.admin_unit = get_current_admin_unit()

        self.columns = self.update_column_dict(
            OrderedDict((each.id, each) for each in self.get_columns())
        )

        self.items = []

    def get_columns(self):
        """Returns the table configuration, a list of column configs.
        """
        raise NotImplementedError()

    def update_column_dict(self, columns):
        return columns

    def get_widths(self):
        """"Returns a list of the column widths as strings"""
        return [col.width for col in self.columns.values()]

    def get_labels(self):
        """"Returns a list of the column labels of the listing"""
        return [col.label for col in self.columns.values()]

    def get_rows(self):
        """"Returns a list of the data for each row of the listing"""
        return [self.get_row_for_item(item) for item in self.items]

    def get_listing(self, items=None):
        if items is not None:
            self.items += items

        if len(self.items) == 0:
            return None
        else:
            return self.latex_view.convert(self.template())

    def get_row_for_item(self, item):
        data = []
        for column in self.columns.values():
            data.append(column.get_value(item))

        return data

    def get_responsible(self, brain):
        return Actor.lookup(brain.responsible).get_label_with_admin_unit()

    def get_repository_title(self, brain):
        """Returns the title of the first parental repository folder.
        """

        # The breadcrumb_titles index was removed in favor of 30% performance
        # improvement while reindexing, thus we now walk up to the
        # repository folder.

        obj = brain.getObject()
        while obj != api.portal.get():
            if IRepositoryFolder.providedBy(obj):
                break
            else:
                obj = obj.aq_parent

        return obj.Title()

    @staticmethod
    def reset_column_widths(columns):
        """recalculates the column widths so that they span the whole textwidth.
        """
        total_width = reduce(lambda total_width, column: total_width + column.get_width(),
                             columns.values(), 0)
        for column in columns.values():
            column.width = str(column.get_width() / total_width * 100) + "%"
        return columns


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class DossiersLaTeXListing(LaTexListing):

    template = ViewPageTemplateFile('templates/listing.pt')

    def get_responsible(self, brain):
        return Actor.lookup(brain.responsible).get_label_with_admin_unit()

    def get_columns(self):
        return [
            Column('reference',
                   _('label_reference_number', default='Reference number'),
                   '10%'),

            Column('sequence_number',
                   _('short_label_sequence_number', default='No.'),
                   '5%'),

            Column('repository_title',
                   _('label_repository_title', default='Repositoryfolder'),
                   '20%',
                   self.get_repository_title),

            Column('title',
                   _('label_title', default='Title'),
                   '25%',
                   'Title'),

            Column('responsible',
                   _('label_responsible', default='Responsible'),
                   '20%',
                   self.get_responsible),

            Column('review_state',
                   _('label_review_state', default='State'),
                   '10%',
                   lambda brain: workflow_state(brain, brain.review_state)),

            Column('start',
                   _('label_start', default='Start'),
                   '5%',
                   lambda brain: helper.readable_date(brain, brain.start)),

            Column('end',
                   _('label_end', default='End'),
                   '5%',
                   lambda brain: helper.readable_date(brain, brain.end))
        ]


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class SubDossiersLaTeXListing(DossiersLaTeXListing):

    def update_column_dict(self, columns):
        del columns['reference']
        del columns['repository_title']
        self.reset_column_widths(columns)
        return columns


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class DocumentsLaTeXListing(DossiersLaTeXListing):

    def get_columns(self):
        return [
            Column('sequence_number',
                   _('short_label_sequence_number', default='No.'),
                   '6%'),

            Column('title',
                   _('label_title', default='Title'),
                   '35%',
                   'Title'),

            Column('document_date',
                   _('label_document_date', default='Document date'),
                   '13%',
                   lambda brain: helper.readable_date(brain, brain.document_date)),

            Column('receipt_date',
                   _('label_receipt_date', default='Receipt date'),
                   '13%',
                   lambda brain: helper.readable_date(brain, brain.receipt_date)),

            Column('delivery_date',
                   _('label_delivery_date', default='Delivery date'),
                   '13%',
                   lambda brain: helper.readable_date(brain, brain.delivery_date)),

            Column('document_author',
                   _('label_document_author', default='Document author'),
                   '20%')
        ]


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class TasksLaTeXListing(DossiersLaTeXListing):

    def get_columns(self):
        return [
            Column('sequence_number',
                   _('short_label_sequence_number', default='No.'),
                   '3%'),

            Column('task_type',
                   _('label_task_type', default='Task type'),
                   '20%',
                   lambda item: task_type_helper(item, item.task_type)),

            Column('issuer',
                   _('label_issuer', default='Issuer'),
                   '15%',
                   lambda item: get_issuer_of_task(item, with_client=True,
                                                   with_principal=False)),

            Column('responsible',
                   _('label_task_responsible', default='Responsible'),
                   '15%',
                   get_responsible_of_task),

            Column('review_state',
                   _('label_review_state', default='State'),
                   '7%',
                   lambda item: workflow_state(item, item.review_state)),

            Column('title',
                   _('label_title', default='Title'),
                   '25%'),

            Column('deadline',
                   _('label_deadline', default='Deadline'),
                   '15%',
                   lambda item: helper.readable_date(item, item.deadline))
        ]


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class TaskHistoryLaTeXListing(LaTexListing):

    def get_actor_label(self, item):
        return Actor.lookup(item.creator).get_label()

    def get_columns(self):
        return [
            Column('created',
                   _('label_time', default=u'Time'),
                   '10%',
                   lambda item: helper.readable_date_time(item, item.created),
                   "left"),

            Column('creator',
                   _('label_creator', default='Changed by'),
                   '20%',
                   self.get_actor_label,
                   "left"),

            Column('transition',
                   _('label_transition', default='Transition'),
                   '20%',
                   lambda item: activity_mf(item.transition),
                   "left"),

            Column('text',
                   _('label_description', default='Description'),
                   '50%'),
        ]


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class JournalLaTeXListing(LaTexListing):

    template = ViewPageTemplateFile('templates/listing.pt')

    def get_actor_label(self, item):
        return Actor.lookup(item.get('actor')).get_label()

    def get_journal_comment(self, item):
        """Skip comment for document sent entries.
        """
        if item.get('action', {}).get('type') == DOCUMENT_SENT:
            return

        return item.get('comments')

    def get_columns(self):
        return [
            Column('time',
                   journal_mf('label_time', default=u'Time'),
                   '10%',
                   lambda item: helper.readable_date_time(item, item.get('time'))),

            Column('title',
                   journal_mf('label_title', default=u'Title'),
                   '45%',
                   lambda item: title_helper(item, item['action'].get('title'))),

            Column('actor',
                   journal_mf('label_actor', default=u'Changed by'),
                   '15%',
                   self.get_actor_label),

            Column('comments',
                   journal_mf('label_comments', default='Comments'),
                   '30%',
                   self.get_journal_comment)
        ]
