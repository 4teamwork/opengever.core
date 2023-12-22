from opengever.api.solr_query_service import SolrFieldMapper
from opengever.base.browser.reporting_view import SolrReporterView
from opengever.base.reporter import readable_actor
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.meeting import _
from Products.statusmessages.interfaces import IStatusMessage


class ProposalReporterFieldMapper(SolrFieldMapper):

    def is_allowed(self, field_name):
        return (
            field_name in self.field_mapping.keys()
            or self.is_dynamic(field_name)
        )


class ProposalReporter(SolrReporterView):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected proposals (paths in request)
    and their important attributes.
    """

    filename = 'proposal_report.xlsx'

    field_mapper = ProposalReporterFieldMapper

    corresponding_listing_name = 'proposals'

    column_settings = [
        {
            'id': 'title',
            'is_default': True,
        },
        {
            'id': 'created',
            'is_default': True,
        },
        {
            'id': 'review_state',
            'is_default': True,
            'alias': 'review_state_label',
            'transform': StringTranslater(None, 'plone').translate,
        },
        {
            'id': 'issuer',
            'is_default': True,
            'title': _(u'label_issuer', default='Issuer'),
            'transform': readable_actor,
        },
        {
            'id': 'responsible',
            'is_default': True,
            'title': _(u'label_comittee', default='Comittee'),
            'transform': readable_actor,
        },
        {
            'id': 'containing_dossier',
            'is_default': True,
            'title': _(u'label_dossier', default=u'Dossier'),
        },
        {
            'id': 'description',
            'is_default': True,
        },
    ]

    def __call__(self):

        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        # XXX: Also make pseudo-relative paths work
        # (as sent by the new gever-ui)
        rewrite_path_list_to_absolute_paths(self.request)

        proposals = self.get_selected_items()

        reporter = XLSReporter(self.request, self.columns(), proposals, field_mapper=self.fields)
        return self.return_excel(reporter)
