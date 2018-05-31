from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.meeting import _
from plone import api
from zExceptions import NotFound


class ProposalTransitionController(object):

    @classmethod
    def url_for(cls, context, transition):
        return '%s/addcomment?form.widgets.transition=%s' % (
            context.absolute_url(),
            transition)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def execute_transition(self, transition, text=None):
        if self.context.contains_checked_out_documents():
            msg = _(u'error_must_checkin_documents_for_transition',
                    default=u'Cannot change the state because the proposal contains checked'
                    u' out documents.')
            api.portal.show_message(message=msg,
                                    request=self.request,
                                    type='error')
            return self.redirect()

        if not self.is_valid_transition(transition):
            raise NotFound
        self.context.execute_transition(transition, text)
        if transition == 'submitted-pending':
            return self.redirect(to_parent=True)
        else:
            return self.redirect()

    def is_valid_transition(self, transition_name):
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False

        return self.context.can_execute_transition(transition_name)

    def redirect(self, to_parent=False):
        if to_parent:
            url = aq_parent(aq_inner(self.context)).absolute_url()
        else:
            url = self.context.absolute_url()
        response = self.request.RESPONSE
        if response.status != 302:  # only redirect if not already redirecting
            return response.redirect(url)
