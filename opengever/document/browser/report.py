from opengever.api.solr_query_service import SolrFieldMapper
from opengever.base.browser.reporting_view import SolrReporterView
from opengever.base.reporter import DATETIME_NUMBER_FORMAT
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.solr.fields import translate_document_type
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.document import _
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from Products.statusmessages.interfaces import IStatusMessage


class DocumentReporterFieldMapper(SolrFieldMapper):

    propertysheet_field = IDocumentCustomProperties['custom_properties']

    def is_allowed(self, field_name):
        return (
            field_name in self.field_mapping.keys()
            or self.is_dynamic(field_name)
        )


class DocumentReporter(SolrReporterView):
    """View that generates an excel spreadsheet with the XLSReporter,
    listing the selected documents (paths in request)
    and their important attributes.
    """

    filename = 'document_report.xlsx'

    field_mapper = DocumentReporterFieldMapper

    column_settings = [
        {
            'id': 'reference',
            'is_default': True,
            'tabbedview_column': 'reference',
        },
        {
            'id': 'sequence_number',
            'is_default': True,
        },
        {
            'id': 'title',
            'is_default': True,
        },
        {
            'id': 'document_author',
            'is_default': True,
            'transform': readable_author,
            'tabbedview_column': 'sortable_author',
        },
        {
            'id': 'document_date',
            'is_default': True,
        },
        {
            'id': 'receipt_date',
            'is_default': True,
        },
        {
            'id': 'delivery_date',
            'is_default': True,
        },
        {
            'id': 'checked_out',
            'is_default': True,
            'title': _(u'label_document_checked_out_by'),
            'transform': readable_author,
            'alias': 'checked_out_fullname',
        },
        {
            'id': 'public_trial',
            'is_default': True,
            'transform': StringTranslater(None, 'opengever.base').translate,
        },
        {
            'id': 'containing_dossier',
            'is_default': True,
        },
        {
            'id': 'document_type',
            'is_default': False,
            'alias': 'document_type_label',
            'transform': translate_document_type,
        },
        {
            'id': 'changed',
            'is_default': False,
            'number_format': DATETIME_NUMBER_FORMAT,
        }
    ]

    def __call__(self):
        if not self.request.get('paths') and not self.request.get('listing_name'):
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        # XXX: Also make pseudo-relative paths work
        # (as sent by the new gever-ui)
        rewrite_path_list_to_absolute_paths(self.request)

        documents = self.get_selected_items()
        reporter = XLSReporter(self.request, self.columns(), documents, field_mapper=self.fields)
        return self.return_excel(reporter)
