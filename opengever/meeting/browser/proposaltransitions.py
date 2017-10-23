from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.meeting import _
from plone import api
from plone.protect.utils import addTokenToUrl
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from z3c.form.field import Fields
from z3c.form.form import button
from z3c.form.form import Form
from zExceptions import NotFound
from zope import schema
from zope.interface import Interface


class ProposalTransitionController(BrowserView):

    @classmethod
    def url_for(cls, context, transition):
        return addTokenToUrl("{}/@@proposaltransitioncontroller?transition={}".format(
            context.absolute_url(), transition))

    def __call__(self):
        if self.context.contains_checked_out_documents():
            msg = _(u'error_must_checkin_documents_for_transition',
                    default=u'Cannot change the state because the proposal contains checked'
                    u' out documents.')
            api.portal.show_message(message=msg,
                                    request=self.request,
                                    type='error')
            return self.redirect_to_proposal()

        transition = self.request.get('transition')
        if not self.is_valid_transition(transition):
            raise NotFound

        self.execute_transition(transition)
        return self.redirect_to_proposal()

    def is_valid_transition(self, transition_name):
        if not api.user.has_permission('Modify portal content', obj=self.context):
            return False

        return self.context.can_execute_transition(transition_name)

    def execute_transition(self, transition_name):
        return self.context.execute_transition(transition_name)

    def redirect_to_proposal(self):
        response = self.request.RESPONSE
        if response.status != 302:  # only redirect if not already redirecting
            return response.redirect(self.context.absolute_url())


class IRejectProposalSchema(Interface):

    text = schema.Text(
        title=_(u'label_reject_proposal_text', default=u'Comment'),
        description=_(u'help_reject_proposal_text',
                      default=u'Describe, why the proposal is rejected'),
        required=False)


class RejectProposalForm(Form):
    fields = Fields(IRejectProposalSchema)
    ignoreContext = True
    label = _(u'heading_reject_proposal_form', u'Reject proposal')

    @button.buttonAndHandler(_(u'reject', default=u'Reject'))
    def reject_handler(self, action):
        data, errors = self.extractData()
        if len(errors) > 0:
            return

        self.reject_proposal(data['text'])
        committee = aq_parent(aq_inner(self.context))

        api.portal.show_message(
            _(u"The proposal has been rejected successfully"),
            request=self.request)
        self.redirect(committee)

    def reject_proposal(self, text):
        self.context.reject(text)

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def cancel(self, action):
        return self.redirect(self.context)

    def redirect(self, content):
        return self.request.RESPONSE.redirect(content.absolute_url())


class RejectProposalView(layout.FormWrapper):

    form = RejectProposalForm
