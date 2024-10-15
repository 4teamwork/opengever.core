from opengever.api.solr_query_service import SolrFieldMapper
from opengever.base.browser.reporting_view import SolrReporterView
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_actor
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.dossier import _
from opengever.dossier.behaviors.customproperties import IDossierCustomProperties
from Products.statusmessages.interfaces import IStatusMessage


class DossierReporterFieldMapper(SolrFieldMapper):

    propertysheet_field = IDossierCustomProperties['custom_properties']

    def is_allowed(self, field_name):
        return (
            field_name in self.field_mapping.keys()
            or self.is_dynamic(field_name)
        )


class DossierReporter(SolrReporterView):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    filename = 'dossier_report.xlsx'

    field_mapper = DossierReporterFieldMapper

    corresponding_listing_name = 'dossiers'

    column_settings = (
        {
            'id': 'title',
            'is_default': True,
        },
        {
            'id': 'start',
            'is_default': True,
            'number_format': DATE_NUMBER_FORMAT,
        },
        {
            'id': 'end',
            'is_default': True,
            'number_format': DATE_NUMBER_FORMAT,
        },
        {
            'id': 'responsible',
            'is_default': True,
            'alias': 'responsible_fullname',
            'transform': readable_actor,
            'title': _(u'dossier_report_responsible', default=u'Responsible')
        },
        {
            'id': 'review_state',
            'is_default': True,
            'alias': 'review_state_label',
            'transform': StringTranslater(None, 'plone').translate,
        },
        {
            'id': 'reference',
            'is_default': True,
            'tabbedview_column': 'reference',
        },
    )

    def __call__(self):
        if not self.request.get('paths') and not self.request.get('listing_name'):
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        # XXX: Also make pseudo-relative paths work
        # (as sent by the new gever-ui)
        rewrite_path_list_to_absolute_paths(self.request)

        dossiers = self.get_selected_items()
        import pdb
        pdb.set_trace()

        reporter = XLSReporter(self.request, self.columns(), dossiers, field_mapper=self.fields)
        return self.return_excel(reporter)
