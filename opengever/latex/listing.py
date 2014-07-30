from ftw.table import helper
from opengever.latex import _
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import get_responsible_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task.helper import task_type_helper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class LatexListing(object):

    template = ViewPageTemplateFile('templates/listing.pt')

    def __init__(self, latex_view, items):
        self.latex_view = latex_view
        self.items = items

        self.admin_unit = get_current_admin_unit()
        self.info = getUtility(IContactInformation)

        # required for template namespace only
        self.request = latex_view.request
        self.context = None

    def get_config(self):
        """Returns the table configuration, a list of dicts for every row,
        containing label, width, getter."""

        raise NotImplementedError()

    def drop_column(self, config, column_id):
        ids = [col.get('id') for col in config]
        config.pop(ids.index(column_id))
        return config

    def get_widths(self):
        """"Returns a LaTEx string with the labels of the listing,
        which are calculated."""
        return [row.get('width') for row in self.get_config()]

    def get_labels(self):
        """"Returns a LaTEx string with the labels of the listing"""
        return [row.get('label') for row in self.get_config()]

    def get_rows(self):
        """"Returns a LaTEx string with all the rows of the listing"""
        return [self.get_row_for_brain(item) for item in self.items]

    def get_listing(self):
        if len(self.items) == 0:
            return None
        else:
            return self.latex_view.convert(self.template())

    def get_row_for_brain(self, brain):
        data = []
        for row in self.get_config():
            data.append(row.get('getter')(brain))

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

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'reference',
             'label': _('label_reference_number', default='Reference number'),
             'width': '10%',
             'getter': lambda brain: brain.reference},

            {'id': 'sequence_number',
             'label': _('short_label_sequence_number', default='No.'),
             'width': '5%',
             'getter': lambda brain: brain.sequence_number},

            {'id': 'repository_title',
             'label': _('label_repository_title', default='Repositoryfolder'),
             'width': '20%',
             'getter': self.get_repository_title},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '25%',
             'getter': lambda brain: brain.Title},

            {'id': 'responsible',
             'label': _('label_responsible', default='Responsible'),
             'width': '20%',
             'getter': self.get_responsible},

            {'id': 'review_state',
             'label': _('label_review_state', default='State'),
             'width': '10%',
             'getter': lambda brain: workflow_state(
                 brain, brain.review_state)},

            {'id': 'start',
             'label': _('label_start', default='Start'),
             'width': '5%',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.start)},

            {'id': 'end',
             'label': _('label_end', default='End'),
             'width': '5%',
             'getter': lambda brain: helper.readable_date(brain, brain.end)}]


class SubDossiersLaTeXListing(DossiersLaTeXListing):

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """
        config = super(SubDossiersLaTeXListing, self).get_config()

        config = self.drop_column(config, 'reference')
        config = self.drop_column(config, 'repository_title')

        return config


class DocumentsLaTeXListing(LatexListing):

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'sequence_number',
             'label': _('short_label_sequence_number', default='No.'),
             'width': '6%',
             'getter': lambda brain: brain.sequence_number},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '35%',
             'getter': lambda brain: brain.Title},

            {'id': 'document_date',
             'label': _('label_document_date', default='Document date'),
             'width': '13%',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.document_date)},

            {'id': 'receipt_date',
             'label': _('label_receipt_date', default='Receipt date'),
             'width': '13%',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.receipt_date)},

            {'id': 'delivery_date',
             'label': _('label_delivery_date', default='Delivery date'),
             'width': '13%',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.delivery_date)},

            {'id': 'document_author',
             'label': _('label_document_author', default='Document author'),
             'width': '20%',
             'getter': lambda brain: brain.document_author}]


class TasksLaTeXListing(LatexListing):

    def get_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'sequence_number',
             'label': _('short_label_sequence_number', default='No.'),
             'width': '3%',
             'getter': lambda item: item.sequence_number},

            {'id': 'task_type',
             'label': _('label_task_type', default='Task type'),
             'width': '20%',
             'getter': lambda item: task_type_helper(item, item.task_type)},

            {'id': 'issuer',
             'label': _('label_issuer', default='Issuer'),
             'width': '15%',
             'getter': lambda item: get_issuer_of_task(
                 item, with_client=True, with_principal=False)},

            {'id': 'responsible',
             'label': _('label_task_responsible', default='Responsible'),
             'width': '15%',
             'getter': lambda item: get_responsible_of_task(item)},

            {'id': 'review_state',
             'label': _('label_review_state', default='State'),
             'width': '7%',
             'getter': lambda item: workflow_state(
                 item, item.review_state)},

            {'id': 'title',
             'label': _('label_title', default='Title'),
             'width': '25%',
             'getter': lambda item: item.title},

            {'id': 'deadline',
             'label': _('label_deadline', default='Deadline'),
             'width': '15%',
             'getter': lambda item: helper.readable_date(
                 item, item.deadline)}]
