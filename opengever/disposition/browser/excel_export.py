from five import grok
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.reporter import get_date_style
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.disposition import _
from opengever.disposition.interfaces import IDisposition
from opengever.dossier import _ as base_mf
from opengever.dossier import _ as dossier_mf
from plone import api


class DispositionExcelExport(grok.View):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    grok.context(IDisposition)
    grok.name('xlsx')
    grok.require('zope2.View')

    def get_attributes(self):
        return [
            {'id': 'reference_number',
             'title': dossier_mf(u'label_reference_number',
                                 default=u'Reference Number')},
            {'id': 'title',
             'title': dossier_mf('label_title', default=u'title')},
            {'id': 'start',
             'title': dossier_mf(u'label_start', default=u'Opening Date'),
             'style': get_date_style()},
            {'id': 'end',
             'title': dossier_mf(u'label_end', default=u'Closing Date'),
             'style': get_date_style()},
            {'id': 'public_trial',
             'title': base_mf(u'label_public_trial', default=u'Public Trial'),
             'transform': StringTranslater(self.request, 'opengever.base').translate},
            {'id': 'archival_value',
             'title': base_mf(u'label_archival_value', default=u'Archival value'),
             'transform': StringTranslater(self.request, 'opengever.base').translate},
            {'id': 'archival_value_annotation',
             'title': base_mf(u'label_archival_value_annotation',
                              default=u'archivalValueAnnotation'),
             'transform': StringTranslater(self.request, 'opengever.base').translate},
            {'id': 'appraisal',
             'title': base_mf(u'label_appraisal', default=u'Appraisal')},
        ]

    def render(self):
        reporter = XLSReporter(
            self.request, self.get_attributes(),
            self.context.get_dossier_representations(),
            sheet_title='Angebot XY', footer=u'mein footer')

        data = reporter()
        if not data:
            msg = _(u'The report could not been generated.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader('Content-Type', 'application/vnd.ms-excel')
        set_attachment_content_disposition(self.request, "dossier_report.xls")

        return data
