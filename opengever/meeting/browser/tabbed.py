from opengever.meeting import _
from opengever.tabbedview import ModelProxyTabbedView


class CommitteeTabbedView(ModelProxyTabbedView):

    def _get_tabs(self):
        return [{
            'id': 'overview',
            'title': _(u'overview', default=u'Overview'),
            }, {
            'id': 'meetings',
            'title': _(u'meetings', default=u'Meetings'),
            }, {
            'id': 'submittedproposals',
            'title': _(u'submittedproposals', default=u'Submitted Proposals'),
            }, {
            'id': 'memberships',
            'title': _(u'memberships', default=u'Memberships'),
            }, {
            'id': 'periods',
            'title': _(u'periods', default=u'Periods'),
            }
        ]
