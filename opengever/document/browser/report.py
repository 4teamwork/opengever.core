from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.reporter import readable_author
from opengever.base.reporter import readable_date
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.document import _
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class DocumentReporter(BaseReporterView):
    """View that generates an excel spreadsheet with the XLSReporter,
    listing the selected documents (paths in request)
    and their important attributes.
    """

    filename = 'document_report.xlsx'

    @property
    def _columns(self):
        return [
            {'id': 'reference',
             'title': _(u'label_document_reference_number')},
            {'id': 'sequence_number',
             'title': _(u'label_document_sequence_number')},
            {'id': 'Title',
             'sort_index': 'sortable_title',
             'title': _(u'label_title', default=u'Title')},
            {'id': 'document_author',
             'title': _(u'label_author', default=u'Author'),
             'sort_index': 'sortable_author',
             'transform': readable_author},
            {'id': 'document_date',
             'title': _(u'label_document_date', default=u'Document Date'),
             'transform': readable_date},
            {'id': 'receipt_date',
             'title': _(u'label_document_receipt_date'),
             'transform': readable_date},
            {'id': 'delivery_date',
             'title': _(u'label_document_delivery_date'),
             'transform': readable_date},
            {'id': 'checked_out',
             'title': _(u'label_document_checked_out_by'),
             'transform': readable_author},
            {'id': 'public_trial',
             'title': _(u'label_public_trial'),
             'transform': StringTranslater(
                 self.request, 'opengever.base').translate},
            {'id': 'containing_dossier',
             'title': _(u'label_dossier_title')},
        ]

    def get_selected_documents(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        documents = []
        for path in self.request.get('paths'):
            documents.append(
                catalog(path={'query': path, 'depth': 0})[0]
                )
        return documents

    def __call__(self):
        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        documents = self.get_selected_documents()
        reporter = XLSReporter(self.request, self.columns(), documents)
        return self.return_excel(reporter)
