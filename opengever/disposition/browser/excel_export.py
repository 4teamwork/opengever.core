from opengever.base import _ as base_mf
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.disposition import _
from opengever.dossier import _ as dossier_mf
from openpyxl.workbook.child import INVALID_TITLE_REGEX
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.size import byteDisplay
import re


def readable_appraisal(value):
    if value is None:
        return value
    elif value:
        label = ARCHIVAL_VALUE_WORTHY
    else:
        label = ARCHIVAL_VALUE_UNWORTHY

    return translate(label, domain="opengever.base", context=getRequest())


class DispositionExcelExport(BrowserView):
    """View that generates an excel spreadsheet for the disposition.

    The generated files lists the selected dossiers (paths in request) and
    their important attributes.
    """

    def get_attributes(self):
        return [
            {'id': 'reference_number',
             'title': dossier_mf(u'label_reference_number',
                                 default=u'Reference Number')},
            {'id': 'title',
             'title': dossier_mf('label_title', default=u'title')},
            {'id': 'start',
             'title': dossier_mf(u'label_start', default=u'Opening Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'end',
             'title': dossier_mf(u'label_end', default=u'Closing Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'public_trial',
             'title': base_mf(u'label_public_trial', default=u'Public Trial'),
             'transform': StringTranslater(
                 self.request, 'opengever.base').translate},
            {'id': 'archival_value',
             'title': base_mf(u'label_archival_value',
                              default=u'Archival value'),
             'transform': StringTranslater(
                 self.request, 'opengever.base').translate},
            {'id': 'archival_value_annotation',
             'title': base_mf(u'label_archival_value_annotation',
                              default=u'archivalValueAnnotation'),
             'transform': StringTranslater(
                 self.request, 'opengever.base').translate},
            {'id': 'docs_count',
             'title': _(u'label_docs_count', default=u'Documents')},
            {'id': 'docs_size',
             'title': _(u'label_docs_size', default=u'Size'),
             'transform': self.human_readable_size},
            {'id': 'appraisal',
             'title': _(u'label_appraisal', default=u'Appraisal'),
             'transform': readable_appraisal},
        ]

    def __call__(self):
        reporter = XLSReporter(
            self.request, self.get_attributes(),
            self.context.get_dossier_representations(),
            sheet_title=self.get_sheet_title())

        response = self.request.RESPONSE
        data = reporter()
        if not data:
            msg = _(u'The report could not been generated.')
            api.portal.show_message(
                message=msg, request=self.request, type='error')
            return response.redirect(self.context.absolute_url())

        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(
            self.request, self.get_file_name())

        return data

    def get_file_name(self):
        """Returns the filename for the excel spreadsheet.
        """
        normalizer = getUtility(IIDNormalizer)
        name_basis = _(u'appraisal_list', default=u'appraisal_list')
        file_name = "{0}_{1}.xlsx".format(
            translate(name_basis, context=self.request),
            normalizer.normalize(self.context.title_or_id()))
        return file_name

    def get_sheet_title(self):
        """Returns current disposition title. Crop it to 30 characters
        because openpyxl only accepts sheet titles with max 30 characters.
        """
        return re.sub(INVALID_TITLE_REGEX, '', self.context.title[:30])

    def human_readable_size(self, size_bytes):
        return translate(byteDisplay(size_bytes), size_bytes, context=self.request)
