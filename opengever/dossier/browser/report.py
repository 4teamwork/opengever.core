from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.base.reporter import value
from opengever.dossier import _
from Products.CMFCore.utils import getToolByName
from opengever.base.browser.reporting_view import BaseReporterView
from Products.statusmessages.interfaces import IStatusMessage


class DossierReporter(BaseReporterView):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    @property
    def _attributes(self):
        return [
            {'id': 'Title',
             'sort_index': 'sortable_title',
             'title': _('label_title', default=u'Title'),
             'transform': value},
            {'id': 'start',
             'title': _(u'label_start', default=u'Opening Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'end',
             'title': _(u'label_end', default=u'Closing Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'responsible',
             'title': _(u'label_responsible', default='Responsible'),
             'transform': readable_author},
            {'id': 'review_state',
             'title': _('label_review_state', default='Review state'),
             'transform': StringTranslater(self.request, 'plone').translate},
            {'id': 'reference',
             'title': _(u'label_reference_number',
                        default=u'Reference Number')},
        ]

    def get_selected_dossiers(self):
        # get the given dossiers
        catalog = getToolByName(self.context, 'portal_catalog')
        dossiers = []
        for path in self.request.get('paths'):
            dossiers.append(
                catalog(path={'query': path, 'depth': 0})[0]
                )
        return dossiers

    def __call__(self):

        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        dossiers = self.get_selected_dossiers()

        # generate the xls data with the XLSReporter
        reporter = XLSReporter(
            self.request, self.attributes(), dossiers)

        data = reporter()
        if not data:
            msg = _(u'Could not generate the report.')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE

        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(self.request, "dossier_report.xlsx")

        return data
