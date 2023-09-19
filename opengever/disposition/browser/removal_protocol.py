from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.disposition import _
from opengever.latex.listing import Column
from opengever.latex.listing import ILaTexListing
from opengever.latex.listing import LaTexListing
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


class IRemovalProtocolLayer(Interface):
    """Request layer for selecting the disposition removal protocol view.
    """


class RemovalProtocol(ExportPDFView):

    request_layer = IRemovalProtocolLayer

    def __call__(self):
        provide_request_layer(self.request, self.request_layer)
        return super(RemovalProtocol, self).__call__()

    def get_build_arguments(self):
        args = super(RemovalProtocol, self).get_build_arguments()
        args['filename'] = self.get_pdf_title()
        return args

    def get_pdf_title(self):
        title = _(u'title_removal_protocol',
                  default=u'Removal protocol for ${disposition}',
                  mapping={'disposition': self.context.title})
        return translate(title, context=self.request)


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class DestroyedDossierListing(LaTexListing):

    def get_archived_label(self, item):
        if item.appraisal:
            return _(u'label_yes', default=u'Yes')

        return _(u'label_no', default=u'No')

    def get_columns(self):
        return [
            Column('reference_number',
                   _('label_reference_number', default='Reference number'),
                   '20%'),

            Column('title',
                   _('label_title', default='Title'),
                   '70%'),

            Column('appraisal',
                   _('label_archived', default='Archived'),
                   '10%',
                   self.get_archived_label)
        ]


@implementer(ILaTexListing)
@adapter(Interface, Interface, Interface)
class DispositionHistoryLaTeXListing(LaTexListing):

    def get_columns(self):
        return [
            Column('date',
                   _('label_time', default=u'Time'),
                   '20%'),

            Column('actor_label',
                   _('label_actor', default=u'Actor'),
                   '40%'),

            Column('transition_label',
                   _('label_action', default=u'Action'),
                   '40%')
        ]


@adapter(Interface, IRemovalProtocolLayer, ILaTeXLayout)
class RemovalProtocolLaTeXView(MakoLaTeXView):

    template_directories = ['latex_templates']
    template_name = 'removal_protocol.tex'

    def translate(self, msg):
        return translate(msg, context=self.request)

    def get_render_arguments(self):
        self.layout.show_contact = False

        dossier_listener = getMultiAdapter(
            (self.context, self.request, self),
            ILaTexListing, name='destroyed_dossiers')

        history_listener = getMultiAdapter(
            (self.context, self.request, self),
            ILaTexListing, name='disposition_history')

        return {
            'label_protocol': self.translate(
                _('label_removal_protocol', default="Removal protocol")),
            'title': self.context.title,
            'disposition_metadata': self.get_disposition_metadata(),
            'label_dossiers': translate(
                _('label_dossiers', default="Dossiers"), context=self.request),
            'dossier_listing': dossier_listener.get_listing(
                self.context.get_dossier_representations()),
            'label_history': translate(
                _('label_history', default="History"), context=self.request),
            'history': history_listener.get_listing(
                reversed(self.context.get_history()))
        }

    def get_disposition_metadata(self):
        rows = []
        config = [
            {'label': _('label_title', default=u'Title'),
             'value': self.context.title},
            {'label': _('label_transfer_number',
                        default=u'Transfer number'),
             'value': self.context.transfer_number
             if self.context.transfer_number else u''}
        ]

        for row in config:
            label = translate(row.get('label'), context=self.request)
            row_label = safe_unicode(self.convert_plain(label))
            value = safe_unicode(row.get('value'))
            rows.append(u'\\bf {} & {} \\\\%%'.format(row_label, value))

        return u'\n'.join(rows)
