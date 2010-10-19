from Products.CMFCore.utils import getToolByName
from opengever.latex.template import LatexTemplateFile
from plonegov.pdflatex.browser.aspdf import AsPDFView
from opengever.latex.layouts.zug_default import ZugDefaultLayout


class DossierListingPDF(AsPDFView):
    """Listing of all dossiers as PDF (recursive). Is called from
    a tabbed view or folder_contents and expects "paths" to be in
    the request.
    """

    render = LatexTemplateFile('dossierlisting_content.tex')

    def __call__(self, *args, **kwargs):
        kwargs['default_book_settings'] = False
        kwargs['pre_compiler'] = ZugDefaultLayout(show_contact=False)
        return AsPDFView.__call__(self, *args, **kwargs)

    def _generate_latex(self, *a, **kw):
        """We do not render the context but a catalog query.
        """
        # generate body late
        latex_body = self.render(rows=self.get_listing_rows())
        self.latex_properties['latex_body'] = latex_body
        # generate document
        generator = self.latex_generator(self.context)
        latex_doc = generator.generate(**self.latex_properties)
        return latex_doc

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
            data.append(' & '.join((
                        '1',
                        'OG-RR-2010-1',
                        'Allgemeines',
                        'Lorem ipsum dolor sit amet',
                        'SKA.ARCH / Debenath Olivier',
                        'Offen',
                        '23.07.2010'
                        )))

        if len(data):
            # we want a \\ and \hline after EVERY line, so lets add a empty
            # entry
            data.append('')

        return '\\\\ \\hline\n'.join(data)


