from contextlib import contextmanager
from copy import deepcopy
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.journal.manager import JournalManager
from opengever.latex import _
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.listing import ILaTexListing
from operator import itemgetter
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import noLongerProvides


class IDossierJournalLayer(ILandscapeLayer):
    """Dossier journal request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


@contextmanager
def provide_dossier_journal_layer(request):
    try:
        provide_request_layer(request, IDossierJournalLayer)
        yield
    finally:
        noLongerProvides(request, IDossierJournalLayer)


class DossierJournalPDFView(ExportPDFView):

    def __call__(self):
        # use the landscape layout
        # let the request provide IDossierJournalLayer
        with provide_dossier_journal_layer(self.request):
            return super(DossierJournalPDFView, self).__call__()

    def get_data(self):
        # let the request provide IDossierJournalLayer
        with provide_dossier_journal_layer(self.request):
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

        title = translate(
            _(
                'label_dossier_journal',
                default=u'Journal of dossier "${title} (${reference_number})"',
                mapping={
                    'title': self.context.title,
                    'reference_number': self.context.get_reference_number(),
                },
            ),
            context=self.request,
        )
        title = self.convert_plain(title)

        return {
            'label': title,
            'listing': journal_listing.get_listing(self.get_journal_data())}

    def get_journal_data(self):
        subdossiers = self.context.get_subdossiers(unrestricted=True, sort_on='path')
        all_dossiers = [self.context] + [b._unrestrictedGetObject() for b in subdossiers]

        all_entries = []
        for dossier in all_dossiers:
            if IAnnotationsJournalizable.providedBy(dossier):
                entries = JournalManager(dossier).list()

                for entry in entries:
                    entry = deepcopy(entry)
                    entry['reference_number'] = dossier.get_reference_number()
                    all_entries.append(entry)

        all_entries.sort(key=itemgetter('time'))
        return all_entries
