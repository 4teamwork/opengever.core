from collections import OrderedDict
from ftw.table import helper
from opengever.latex import _
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import get_responsible_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task.helper import task_type_helper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Column(object):

    def __init__(self, id, label, width, getter=None):
        self.id = id
        self.label = label
        self.width = width

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


class LatexListing(object):

    template = ViewPageTemplateFile('templates/listing.pt')

    def __init__(self, latex_view, items):
        self.latex_view = latex_view
        self.items = items

        self.admin_unit = get_current_admin_unit()

        self.columns = self.update_column_dict(
            OrderedDict((each.id, each) for each in self.get_columns())
        )

        # required for template namespace only
        self.request = latex_view.request
        self.context = None

    def get_columns(self):
        """Returns the table configuration, a list of column configs.
        """
        raise NotImplementedError()

    def update_column_dict(self, columns):
        return columns

    def get_widths(self):
        """"Returns a LaTEx string with the labels of the listing,
        which are calculated."""
        return [col.width for col in self.columns.values()]

    def get_labels(self):
        """"Returns a LaTEx string with the labels of the listing"""
        return [col.label for col in self.columns.values()]

    def get_rows(self):
        """"Returns a LaTEx string with all the rows of the listing"""
        return [self.get_row_for_item(item) for item in self.items]

    def get_listing(self):
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

        # We could either query the catalog for every parent (slow), get the
        # object and walk up (slower), or guess the distance to the first
        # parental repository folder based on the reference number signature
        # (fast). Using the distance we can get title from the breadcrumbs
        # index. So we take the latter, altough it seems a little risky when
        # the reference number concept is changed.

        if '/' not in brain.reference:
            return ''

        # get the last part of the reference number
        dossier_ref_nr = brain.reference.split('/')[-1].strip()

        # multiple nested dossiers are seperated by a dot (.), so count the
        # dots
        distance = len(dossier_ref_nr.split('.')) + 1

        # get the title of the repository folder from the breadcrumb_titles
        return brain.breadcrumb_titles[-distance]['Title']


class DossiersLaTeXListing(LatexListing):

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


class SubDossiersLaTeXListing(DossiersLaTeXListing):

    def update_column_dict(self, columns):
        del columns['reference']
        del columns['repository_title']
        return columns


class DocumentsLaTeXListing(LatexListing):

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
                    lambda brain:
                        helper.readable_date(brain, brain.document_date)),

            Column('receipt_date',
                   _('label_receipt_date', default='Receipt date'),
                   '13%',
                   lambda brain:
                        helper.readable_date(brain, brain.receipt_date)),

            Column('delivery_date',
                   _('label_delivery_date', default='Delivery date'),
                   '13%',
                   lambda brain:
                        helper.readable_date(brain, brain.delivery_date)),

            Column('document_author',
                   _('label_document_author', default='Document author'),
                   '20%')
            ]


class TasksLaTeXListing(LatexListing):

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
