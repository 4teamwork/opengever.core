from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.base.interfaces import IBaseClientID
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.repositoryroot import IRepositoryRoot
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, getAdapter
from zope.interface import Interface


class IDossierCoverLayer(Interface):
    """Request layer for selecting the dossier cover view.
    """


class DossierCoverPDFView(grok.View, ExportPDFView):
    grok.name('dossier_cover_pdf')
    grok.context(IDossierMarker)
    grok.require('zope2.View')

    def render(self):
        provide_request_layer(self.request, IDossierCoverLayer)

        return ExportPDFView.__call__(self)


class DossierCoverLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IDossierCoverLayer, ILaTeXLayout)

    template_directories = ['templates']
    template_name = 'dossiercover.tex'

    def get_render_arguments(self):
        args = {
            'clienttitle': self.convert_plain(self.get_client_title()),
            'repositoryversion': self.convert_plain(
                self.get_repository_version()),
            'referencenr': self.convert_plain(self.get_referencenumber()),
            'title': self.convert_plain(self.context.Title()),
            'description': self.convert(self.get_description()),
            'responsible': self.convert_plain(self.get_responsible()),

            'start': self.convert_plain(self.context.toLocalizedTime(
                    str(IDossier(self.context).start)) or '-'),
            'end': self.convert_plain(self.context.toLocalizedTime(
                    str(IDossier(self.context).end)) or '-'),
            }

        return args

    def get_description(self):
        return self.context.Description().replace('\n', '<br />')

    def get_referencenumber(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_responsible(self):
        return self.context.get_responsible_actor().get_label()

    def get_client_title(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        return proxy.client_title

    def get_repository_version(self):
        obj = self.context
        while not IRepositoryRoot.providedBy(obj):
            obj = aq_parent(aq_inner(obj))

        return obj.version or ''
