from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.disposition import _
from opengever.disposition.disposition import IDisposition
from opengever.latex.listing import Column
from opengever.latex.listing import ILaTexListing
from opengever.latex.listing import LaTexListing
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface


class IRemovalProtocolLayer(Interface):
    """Request layer for selecting the disposition removal protocol view.
    """


class RemovalProtocol(grok.View, ExportPDFView):
    grok.name('removal_protocol')
    grok.context(IDisposition)
    grok.require('zope2.View')

    request_layer = IRemovalProtocolLayer

    def render(self):
        provide_request_layer(self.request, self.request_layer)

        return ExportPDFView.__call__(self)


class DestroyedDossierListing(LaTexListing):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('destroyed_dossiers')

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


class DispositionHistoryLaTeXListing(LaTexListing):
    grok.provides(ILaTexListing)
    grok.adapts(Interface, Interface, Interface)
    grok.name('disposition_history')

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


class RemovalProtocolLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IRemovalProtocolLayer, ILaTeXLayout)

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
            'history': history_listener.get_listing(self.context.get_history())
        }

    def get_disposition_metadata(self):
        rows = []
        config = [
            {'label': _('label_title', default=u'Title'),
             'value': self.context.title},
            {'label': _('label_transfer_number',
                        default=u'Transfer number'),
             'value': self.context.transfer_number if
                 self.context.transfer_number else u''}
        ]

        for row in config:
            label = translate(row.get('label'), context=self.request)
            rows.append(u'\\bf {} & {} \\\\%%'.format(
                self.convert_plain(label), row.get('value')))

        return '\n'.join(rows)
