from five import grok
from Products.CMFCore.utils import getToolByName
from plonegov.pdflatex.browser.aspdf import AsPDFView
from opengever.latex.template import LatexTemplateFile


class DossierListingPDF(AsPDFView, grok.CodeView):
    """Listing of all dossiers as PDF (recursive). Is called from
    a tabbed view or folder_contents and expects "paths" to be in
    the request.
    """

    grok.name('pdf-dossier-listing')

    content_template = LatexTemplateFile('dossierlisting_content.tex')

    def __call__(self, *args, **kwargs):
        kwargs['default_book_settings'] = False
#         kwargs['pre_compiler']
        return super(DossierListingPDF, self).__call__(*args, **kwargs)

    def __generate_latex(self):
        """We do not render the context but a catalog query.
        """
        return self.content_template(rows=self.get_listing_rows())

    def get_listing_rows(self):
        """Returns the listing rows rendered in latex.
        """
        data = []

        # XXX: all dossier types
        types = ('opengever.dossier.businesscasedossier',)
        query = {'path': '/'.join(self.context.getPhysicalPath()),
                 'portal_type': types}
        catalog = getToolByName(self.context, 'portal_catalog')

        for brain in catalog(query):
            # html 2 latex
            data.append(' & '.join(
                    '1',
                    'OG-RR-2010-1',
                    'Allgemeines',
                    'Lorem ipsum dolor sit amet',
                    'SKA.ARCH / Debenath Olivier',
                    'Offen',
                    '23.07.2010'
                    ))

        return '\\\\ \\hline\n'.join(data)


