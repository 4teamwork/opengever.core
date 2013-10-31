from five import grok
from ftw.table import helper
from opengever.latex import _
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import get_responsible_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.task.helper import task_type_helper
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Interface


class ILaTexListing(Interface):

    def get_labels():
        """"Returns a LaTEx string with the labels of the listing"""

    def get_widths():
        """"Returns a LaTEx string with the labels of the listing,
        which are calculated."""

    def get_rows():
        """"Returns a LaTEx string with all the rows of the listing"""

    def get_config():
        """Returns the table configuration, a list of dicts for every row,
        containing label, width, getter."""


class DossiersLaTeXListing(grok.MultiAdapter):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('dossiers')

    def __init__(self, context, request, latex_view):
        self.context = context
        self.request = request
        self.latex_view = latex_view

        self.client = get_current_client()
        self.info = getUtility(IContactInformation)

    def get_widths(self):
        widths = []
        for row in self.get_config():
            widths.append('p{{{}}}'.format(row.get('width')))

        return ''.join(widths)

    def get_labels(self):
        labels = []
        for row in self.get_config():
            label = translate(row.get('label'), context=self.request)
            labels.append(u'\\bfseries {}'.format(label))

        return ' & '.join(labels)

    def get_rows(self, brains):
        rows = []

        for brain in brains:
            rows.append(self.get_row_for_brain(brain))

        return rows

    def get_row_for_brain(self, brain):

        data = []
        for row in self.get_config():
            data.append(row.get('getter')(brain))

        return self.convert_list_to_row(data)

    def convert_list_to_row(self, row):
        data = []

        for cell in row:
            if cell is None:
                data.append('')

            elif isinstance(cell, unicode):
                cell = cell.encode('utf-8')
                data.append(self.latex_view.convert_plain(cell))

            elif isinstance(cell, str):
                data.append(self.latex_view.convert_plain(cell))

            else:
                data.append(self.latex_view.convert_plain(str(cell)))

        return ' & '.join(data)

    def get_responsible(self, brain):
        return '%s / %s' % (
            self.client.title,
            self.info.describe(brain.responsible))

    def get_state(self, brain):
        return brain

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

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'reference',
             'label': _('label_reference_number', default='Reference number'),
             'width': '13mm',
             'getter': lambda brain: brain.reference},

            {'id': 'sequence_number',
             'label': _('label_sequence_number', default='No.'),
             'width': '4mm',
             'getter': lambda brain: brain.sequence_number},

            {'id': 'repository_title',
             'label': _('label_repository_title', default='Repositoryfolder'),
             'width': '40mm',
             'getter': self.get_repository_title},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '50mm',
             'getter': lambda brain: brain.Title},

            {'id': 'responsible',
             'label': _('label_responsible', default='Responsible'),
             'width': '48mm',
             'getter': self.get_responsible},

            {'id': 'review_state',
             'label': _('label_review_state', default='State'),
             'width': '16mm',
             'getter': lambda brain: workflow_state(
                 brain, brain.review_state)},

            {'id': 'start',
             'label': _('label_start', default='Start'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.start)},

            {'id': 'end',
             'label': _('label_end', default='End'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(brain, brain.end)}]


class SubDossiersLaTeXListing(DossiersLaTeXListing):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('subdossiers')

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        config = super(SubDossiersLaTeXListing, self).get_config()

        ids = [col.get('id') for col in config]

        config.pop(ids.index('reference'))
        config.pop(ids.index('repository_title'))

        return config


class DocumentsLaTeXListing(DossiersLaTeXListing):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('documents')

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'sequence_number',
             'label': _('label_sequence_number', default='No.'),
             'width': '4mm',
             'getter': lambda brain: brain.sequence_number},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '50mm',
             'getter': lambda brain: brain.Title},

            {'id': 'document_date',
             'label': _('label_document_date', default='Document date'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.document_date)},

            {'id': 'receipt_date',
             'label': _('label_receipt_date', default='Document date'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.receipt_date)},

            {'id': 'delivery_date',
             'label': _('label_delivery_date', default='Document date'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.delivery_date)},

            {'id': 'document_author',
             'label': _('label_sequence_number', default='No.'),
             'width': '4mm',
             'getter': lambda brain: brain.document_author}]


class TasksLaTeXListing(DossiersLaTeXListing):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('tasks')

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'sequence_number',
             'label': _('label_sequence_number', default='No.'),
             'width': '4mm',
             'getter': lambda brain: brain.sequence_number},

            {'id': 'task_type',
             'label': _('label_task_type', default='Task type'),
             'width': '50mm',
             'getter': lambda brain: task_type_helper(brain, brain.task_type)},

            {'id': 'issuer',
             'label': _('label_issuer', default='Issuer'),
             'width': '10mm',
             'getter': lambda brain: get_issuer_of_task(
                 brain, with_client=True, with_principal=False)},

            {'id': 'responsible',
             'label': _('label_responsible', default='Responsible'),
             'width': '10mm',
             'getter': lambda brain: get_responsible_of_task(brain)},

            {'id': 'review_state',
             'label': _('label_review_state', default='State'),
             'width': '16mm',
             'getter': lambda brain: workflow_state(
                 brain, brain.review_state)},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '50mm',
             'getter': lambda brain: brain.Title},

            {'id': 'deadline',
             'label': _('label_deadline', default='Deadline'),
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.deadline)},

            {'id': 'document_author',
             'label': _('label_sequence_number', default='No.'),
             'width': '4mm',
             'getter': lambda brain: brain.document_author}]
