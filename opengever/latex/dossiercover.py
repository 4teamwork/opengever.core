from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.base.interfaces import IReferenceNumber
from opengever.dossier.behaviors.dossier import IDossier
from opengever.latex import _
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.repository.repositoryroot import IRepositoryRoot
from zope.component import adapter
from zope.component import getAdapter
from zope.i18n import translate
from zope.interface import Interface


class IDossierCoverLayer(Interface):
    """Request layer for selecting the dossier cover view.
    """


class DossierCoverPDFView(ExportPDFView):

    request_layer = IDossierCoverLayer

    def __call__(self):
        provide_request_layer(self.request, self.request_layer)

        return super(DossierCoverPDFView, self).__call__()


@adapter(Interface, IDossierCoverLayer, ILaTeXLayout)
class DossierCoverLaTeXView(MakoLaTeXView):

    template_directories = ['templates']
    template_name = 'dossiercover.tex'
    translatable_labels = {
        'label_responsible': _('label_responsible', default='Responsible'),
        'label_repository_version': _('repository_version', default='Repository version'),
        'label_reference_number': _('label_reference_number', default='Reference number'),
        'label_description': _('label_description', default='Description'),
        'label_start': _('label_start', default='Start'),
        'label_end': _('label_end', default='End'),
    }

    def get_render_arguments(self):
        args = self.get_dossier_metadata()
        args.update(self.get_translated_labels())
        return args

    def get_dossier_metadata(self):
        return {
            'clienttitle': self.convert_plain(self.get_current_admin_unit_label()),
            'repositoryversion': self.convert_plain(self.get_repository_version()),
            'referencenr': self.convert_plain(self.get_referencenumber()),
            'title': self.convert_plain(self.context.Title()),
            'description': self.convert(self.get_description()),
            'responsible': self.convert_plain(self.get_responsible()),
            'start': self.convert_plain(self.context.toLocalizedTime(str(IDossier(self.context).start)) or '-'),
            'end': self.convert_plain(self.context.toLocalizedTime(str(IDossier(self.context).end)) or '-'),
        }

    def get_translated_labels(self):
        labels = {}
        for key, label in self.translatable_labels.items():
            labels[key] = translate(label, context=self.request)
        return labels

    def get_description(self):
        return self.context.Description().replace('\n', '<br />')

    def get_referencenumber(self):
        return getAdapter(self.context, IReferenceNumber).get_number()

    def get_responsible(self):
        return self.context.responsible_label

    def get_current_admin_unit_label(self):
        return get_current_admin_unit().label() or ''

    def get_repository_version(self):
        obj = self.context
        while not IRepositoryRoot.providedBy(obj):
            obj = aq_parent(aq_inner(obj))

        return obj.version or ''
