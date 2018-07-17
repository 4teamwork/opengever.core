from copy import deepcopy
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.latex import _
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.listing import ILaTexListing
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface


class IDossierJournalLayer(ILandscapeLayer):
    """Dossier journal request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class DossierJournalPDFView(ExportPDFView):

    request_layer = IDossierJournalLayer

    def __call__(self):
        # use the landscape layout
        # let the request provide IDossierJournalLayer
        provide_request_layer(self.request, self.request_layer)

        return super(DossierJournalPDFView, self).__call__()

    def get_data(self):
        # let the request provide IDossierJournalLayer
        provide_request_layer(self.request, self.request_layer)

        assembler = getMultiAdapter((self.context, self.request),
                                    IPDFAssembler)
        return assembler.build_pdf()


@adapter(Interface, IDossierJournalLayer, ILaTeXLayout)
class DossierJorunalLaTeXView(MakoLaTeXView):

    template_directories = ['templates', ]
    template_name = 'dossierjournal.tex'

    def get_render_arguments(self):
        self.layout.show_organisation = True

        journal_listing = getMultiAdapter((self.context, self.request, self),
                                          ILaTexListing, name='journal')

        return {
            'label': translate(
                _('label_dossier_journal',
                  default=u'Journal of dossier ${title} (${reference_number})',
                  mapping={'title': self.context.title,
                           'reference_number': self.context.get_reference_number()}),
                context=self.request),
            'listing': journal_listing.get_listing(self.get_journal_data())}

    def get_journal_data(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            data = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
            return deepcopy(data)

        return []
