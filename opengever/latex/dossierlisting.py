from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_selected_items
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from opengever.tabbedview.helper import workflow_state
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import directlyProvidedBy, directlyProvides


class IDossierListingLayer(ILandscapeLayer):
    """Dossier listing request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class DossierListingPDFView(grok.View, ExportPDFView):
    grok.name('pdf-dossier-listing')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        # use the landscape layout
        # let the request provide IDossierListingLayer
        if not IDossierListingLayer.providedBy(self.request):
            ifaces = [IDossierListingLayer] + list(directlyProvidedBy(
                    self.request))
            directlyProvides(self.request, *ifaces)

        return ExportPDFView.__call__(self)


class DossierListingLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IDossierListingLayer, ILaTeXLayout)

    template_directories = ['templates']
    template_name = 'dossierlisting.tex'

    def __init__(self, *args, **kwargs):
        MakoLaTeXView.__init__(self, *args, **kwargs)
        self.info = None
        self.client = None

    def get_render_arguments(self):
        self.layout.show_organisation = True
        self.info = getUtility(IContactInformation)
        self.client = get_current_client()

        return {'rows': self.get_rows()}

    def get_rows(self):
        rows = []

        for brain in get_selected_items(self.context, self.request):
            rows.append(self.get_row_for_brain(brain))

        return rows

    def get_row_for_brain(self, brain):
        reference_number = brain.reference
        sequence_number = brain.sequence_number
        filing_number = getattr(brain, 'filing_no', None)
        repository_title = self.get_repository_title(brain)
        title = brain.Title

        responsible = '%s / %s' % (
            self.client.title,
            self.info.describe(brain.responsible))

        review_state = workflow_state(brain, brain.review_state)
        start_date = helper.readable_date(brain, brain.start)
        end_date = helper.readable_date(brain, brain.end)

        data = (reference_number or '',
                sequence_number or '',
                filing_number or '',
                repository_title or '',
                title or '',
                responsible or '',
                review_state or '',
                start_date or '',
                end_date or '')

        return self.convert_list_to_row(data)

    def convert_list_to_row(self, row):
        data = []

        for cell in row:
            if cell is None:
                data.append('')

            elif isinstance(cell, unicode):
                cell = cell.encode('utf-8')
                data.append(self.convert(cell))

            elif isinstance(cell, str):
                data.append(self.convert(cell))

            else:
                data.append(self.convert(str(cell)))

        return ' & '.join(data)

    def get_repository_title(self, brain):
        """Returns the title of the first parental repository folder.
        """

        # We could either query the catalog for every parent (slow), get the
        # object and walk up (slower), or guess the distance to the first
        # parental repository folder based on the reference number signature
        # (fast). Using the distance we can get title from the breadcrumbs
        # index. So we take the latter, altough it seems a little risky when
        # the reference number concept is changed.

        # get the last part of the reference number
        dossier_ref_nr = brain.reference.split('/')[-1].strip()

        # multiple nested dossiers are seperated by a dot (.), so count the
        # dots
        distance = len(dossier_ref_nr.split('.')) + 1

        # get the title of the repository folder from the breadcrumb_titles
        return brain.breadcrumb_titles[-distance]['Title']
