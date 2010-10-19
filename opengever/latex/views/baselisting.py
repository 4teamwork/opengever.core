from plonegov.pdflatex.browser.aspdf import AsPDFView
from Products.CMFCore.utils import getToolByName
from opengever.latex.layouts.zug_default import ZugDefaultLayout


class BasePDFListing(AsPDFView):
    """Basic view for creating a pdf of object selected in a tabbed view.
    """

    # Latex template file
    template = None

    def __call__(self, *args, **kwargs):
        if 'default_book_settings' not in kwargs:
            kwargs['default_book_settings'] = False
        if 'pre_compiler' not in kwargs:
            kwargs['pre_compiler'] = ZugDefaultLayout(show_contact=False)
        return AsPDFView.__call__(self, *args, **kwargs)

    def _generate_latex(self, *a, **kw):
        """We do not render the context but a catalog query.
        """
        # generate body late
        latex_body = self.render()
        self.latex_properties['latex_body'] = latex_body
        # generate document
        generator = self.latex_generator(self.context)
        latex_doc = generator.generate(**self.latex_properties)
        return latex_doc

    def render(self):
        """Renders the template
        """
        return self.template()

    def get_selected_brains(self):
        """Returns all brains which were selected in the tabbed view.
        """

        catalog = getToolByName(self.context, 'portal_catalog')

        for path in self.request.get('paths', []):
            brains = catalog({'path': {'query': path,
                                       'depth': 0}})
            assert len(brains) == 1
            yield brains[0]
