from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.listing import ILaTexListing
from opengever.latex.utils import get_selected_items_from_catalog
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface


class IDossierListingLayer(ILandscapeLayer):
    """Dossier listing request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class DossierListingPDFView(ExportPDFView):
    request_layer = IDossierListingLayer

    def __call__(self):
        # use the landscape layout
        # let the request provide IDossierListingLayer
        provide_request_layer(self.request, self.request_layer)

        return super(DossierListingPDFView, self).__call__()


@adapter(Interface, IDossierListingLayer, ILaTeXLayout)
class DossierListingLaTeXView(MakoLaTeXView):

    template_directories = ['templates', ]
    template_name = 'dossierlisting.tex'

    def get_render_arguments(self):
        self.layout.show_organisation = True

        brains = [brain for brain in get_selected_items_from_catalog(
            self.context, self.request)]

        dossier_listing = getMultiAdapter((self.context, self.request, self),
                                          ILaTexListing, name='dossiers')

        return {'listing': dossier_listing.get_listing(brains)}
