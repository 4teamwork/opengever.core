from copy import deepcopy
from five import grok
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.latex import _
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.listing import ILaTexListing
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface


class IDossierJournalLayer(ILandscapeLayer):
    """Dossier listing request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class DossierJournalPDFView(grok.View, ExportPDFView):
    grok.name('pdf-dossier-journal')
    grok.context(Interface)
    grok.require('zope2.View')

    request_layer = IDossierJournalLayer

    def render(self):
        # use the landscape layout
        # let the request provide IDossierListingLayer
        provide_request_layer(self.request, self.request_layer)

        return ExportPDFView.__call__(self)

    def get_data(self):
        # let the request provide IDossierListingLayer
        provide_request_layer(self.request, self.request_layer)

        assembler = getMultiAdapter((self.context, self.request),
                                    IPDFAssembler)
        return assembler.build_pdf()


class DossierListingLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IDossierJournalLayer, ILaTeXLayout)

    template_directories = ['templates', ]
    template_name = 'dossierjournal.tex'

    def get_render_arguments(self):
        self.layout.show_organisation = True

        dossier_listing = getMultiAdapter((self.context, self.request, self),
                                          ILaTexListing, name='journal')

        return {
            'label': translate(
                _('label_dossier_journal',
                  default=u'Journal of dossier ${title} (${reference_number})',
                  mapping={'title': self.context.title,
                           'reference_number': self.context.get_reference_number()}),
                context=self.request),
            'listing': dossier_listing.get_listing(self.get_journal_data())}

    def get_journal_data(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            data = annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
            return deepcopy(data)

        return []
