from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.listing import ILaTexListing
from opengever.latex.utils import get_selected_items_from_catalog
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_client
from zope.component import getMultiAdapter
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

    def get_render_arguments(self):
        self.layout.show_organisation = True
        self.info = getUtility(IContactInformation)
        self.client = get_current_client()

        brains = [brain for brain in get_selected_items_from_catalog(
            self.context, self.request)]

        dossier_listing = getMultiAdapter((self.context, self.request, self),
                                          ILaTexListing, name='dossiers')

        return {'listing': dossier_listing.get_listing(brains)}
