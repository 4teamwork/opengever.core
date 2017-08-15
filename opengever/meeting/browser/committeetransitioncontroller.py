from opengever.meeting import _
from plone import api
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView


DEACTIVATE = 'opengever_committee_workflow--TRANSITION--deactivate--active_inactive'  # noqa
REACTIVATE = 'opengever_committee_workflow--TRANSITION--reactivate--inactive_active'  # noqa


class CommitteeTransitionController(BrowserView):
    """Execute workflow transitions for committees.

    XXX: currently duplicates transitions in plone and sql. sql may go away
    though.
    """
    implements(IBrowserView)

    def __init__(self, context, request):
        super(CommitteeTransitionController, self).__init__(context, request)
        self.wf_tool = api.portal.get_tool('portal_workflow')

    def __call__(self):
        transition = self.request.get('transition')
        if not transition:
            raise NotFound

        self.execute_transition(transition)
        self.redirect()

    def redirect(self):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def execute_transition(self, transition_name):
        assert transition_name in (DEACTIVATE, REACTIVATE,)

        if transition_name == DEACTIVATE:
            self.deactivate()
        elif transition_name == REACTIVATE:
            self.reactivate()

    def reactivate(self):
        model = self.context.load_model()
        self.wf_tool.doActionFor(self.context, REACTIVATE)
        model.reactivate()

        api.portal.show_message(
            message=_(u'label_committe_reactivated',
                      default="Committee reactivated successfully"),
            request=self.request, type='info')

    def deactivate(self):
        model = self.context.load_model()
        if model.has_pending_meetings():
            api.portal.show_message(
                message=_('msg_pending_meetings',
                          default=u'Not all meetings are closed.'),
                request=self.request, type='error')

            return self.redirect()

        if model.has_unscheduled_proposals():
            api.portal.show_message(
                message=_('msg_unscheduled_proposals',
                          default=u'There are unscheduled proposals submitted'
                          ' to this committee.'),
                request=self.request, type='error')

            return self.redirect()

        self.wf_tool.doActionFor(self.context, DEACTIVATE)
        model.deactivate()

        api.portal.show_message(
            message=_(u'label_committe_deactivated',
                      default="Committee deactivated successfully"),
            request=self.request, type='info')
