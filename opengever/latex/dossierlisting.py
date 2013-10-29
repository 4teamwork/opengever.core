from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_selected_items_from_catalog
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.latex.utils import workflow_state
from zope.component import getUtility
from zope.interface import Interface


class IDossierListingLayer(ILandscapeLayer):
    """Dossier listing request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class DossierListingPDFView(grok.View, ExportPDFView):
    grok.name('pdf-dossier-listing')
    grok.context(Interface)
    grok.require('zope2.View')

    request_layer = IDossierListingLayer

    def render(self):
        # use the landscape layout
        # let the request provide IDossierListingLayer
        provide_request_layer(self.request, self.request_layer)

        return ExportPDFView.__call__(self)


class DossierListingLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IDossierListingLayer, ILaTeXLayout)

    template_directories = ['templates', ]
    template_name = 'dossierlisting.tex'

    def __init__(self, *args, **kwargs):
        MakoLaTeXView.__init__(self, *args, **kwargs)
        self.info = None
        self.client = None

    def get_table_config(self):
        """Returns a list with dict per row including this row informations:
        - label
        - value_getter
        - width
        """

        return [
            {'id': 'reference',
             'label': 'Aktenzeichen',
             'width': '13mm',
             'getter': lambda brain: brain.reference},
            {'id': 'sequence_number',
             'label': 'Nr.',
             'width': '4mm',
             'getter': lambda brain: brain.sequence_number},
            {'id': 'repository_title',
             'label': 'Ordnungspos.',
             'width': '40mm',
             'getter': self.get_repository_title},
            {'id': 'title',
             'label': 'Titel',
             'width': '50mm',
             'getter': lambda brain: brain.Title},
            {'id': 'responsible',
             'label': 'Federfuhrung',
             'width': '48mm',
             'getter': self.get_responsible},
            {'id': 'review_state',
             'label': 'Status',
             'width': '16mm',
             'getter': lambda brain: workflow_state(
                 brain, brain.review_state)},
            {'id': 'start',
             'label': 'Begin',
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(
                 brain, brain.start)},
            {'id': 'end',
             'label': 'Ende',
             'width': '10mm',
             'getter': lambda brain: helper.readable_date(brain, brain.end)}]

    def get_render_arguments(self):
        self.layout.show_organisation = True
        self.info = getUtility(IContactInformation)
        self.client = get_current_client()

        return {
            'rows': self.get_rows(),
            'widths': self.get_widths(),
            'labels': self.get_labels()}

    def get_rows(self):
        rows = []

        for brain in get_selected_items_from_catalog(
                self.context, self.request):
            rows.append(self.get_row_for_brain(brain))

        return rows

    def get_labels(self):
        labels = []
        for row in self.get_table_config():
            labels.append(
                u'\\bfseries {}'.format(row.get('label')))

        return ' & '.join(labels)

    def get_widths(self):
        widths = []
        for row in self.get_table_config():
            widths.append('p{{{}}}'.format(row.get('width')))

        return ''.join(widths)

    def get_row_for_brain(self, brain):

        data = []
        for row in self.get_table_config():
            data.append(row.get('getter')(brain))

        return self.convert_list_to_row(data)

    def convert_list_to_row(self, row):
        data = []

        for cell in row:
            if cell is None:
                data.append('')

            elif isinstance(cell, unicode):
                cell = cell.encode('utf-8')
                data.append(self.convert_plain(cell))

            elif isinstance(cell, str):
                data.append(self.convert_plain(cell))

            else:
                data.append(self.convert_plain(str(cell)))

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
