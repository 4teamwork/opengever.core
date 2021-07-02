from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.reporter import readable_author
from opengever.base.reporter import readable_date
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.base.reporter import value
from opengever.base.utils import rewrite_path_list_to_absolute_paths
from opengever.meeting import _
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class ProposalReporter(BaseReporterView):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected proposals (paths in request)
    and their important attributes.
    """

    filename = 'proposal_report.xlsx'

    @property
    def _columns(self):
        return [
            {'id': 'Title', 'sort_index': 'sortable_title',
             'title': _('label_title', default=u'Title'), 'transform': value},
            {'id': 'created', 'title': _(u'label_created', default=u'Created'),
             'transform': readable_date},
            {'id': 'review_state', 'title': _('label_review_state', default='Review state'),
             'transform': StringTranslater(self.request, 'plone').translate},
            {'id': 'issuer', 'title': _(u'label_issuer', default='Issuer'),
             'transform': readable_author},
            {'id': 'responsible', 'title': _(u'label_comittee', default='Comittee'),
             'transform': readable_author},
            {'id': 'containing_dossier', 'title': _(u'label_dossier', default=u'Dossier')},
            {'id': 'Description', 'title': _('label_description', default=u'Description')},
        ]

    def get_selected_proposals(self):
        # get the given proposals
        catalog = getToolByName(self.context, 'portal_catalog')
        proposals = []
        for path in self.request.get('paths'):
            proposals.append(
                catalog(path={'query': path, 'depth': 0})[0]
            )
        return proposals

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

        proposals = self.get_selected_proposals()

        reporter = XLSReporter(self.request, self.columns(), proposals)
        return self.return_excel(reporter)
