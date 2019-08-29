from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.meeting import _
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import layout
from Products.CMFPlone import PloneMessageFactory as PMF
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser import radio
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import BadRequest
from zExceptions import NotFound
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def get_transition_vocab(context):
    transitions = []
    for transition in context.get_transitions():
        transitions.append(SimpleVocabulary.createTerm(
            transition.name,
            transition.name,
            PMF(transition.name, default=transition.title)))

    return SimpleVocabulary(transitions)


class IProposalTransitionCommentFormSchemaSQL(Interface):
    """Schema-interface class for the proposal transition comment form
    """
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        source=get_transition_vocab,
        required=False,
        )

    text = schema.Text(
        title=_('label_comment', default="Comment"),
        required=False,
        )


class ProposalTransitionCommentAddFormSQL(form.AddForm, AutoExtensibleForm):

    allow_prefill_from_GET_request = True  # XXX

    fields = field.Fields(IProposalTransitionCommentFormSchemaSQL)
    # keep widget for converters (even though field is hidden)
    fields['transition'].widgetFactory = radio.RadioFieldWidget

    @classmethod
    def url_for(cls, context, transition):
        return '%s/addtransitioncomment_sql?form.widgets.transition=%s' % (
            context.absolute_url(),
            transition)

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

    @property
    def label(self):
        title = self.context.Title().decode('utf-8')
        transition = self.context.workflow.get_transition(self.transition)
        transition_title = translate(transition.title, domain='plone',
                                     context=self.request)
        return u'{}: {}'.format(title, transition_title)

    @property
    def transition(self):
        if not hasattr(self, '_transition'):
            self._transition = self.request.get('form.widgets.transition',
                                                self.request.get('transition'))
            if not self._transition:
                raise BadRequest("A transition is required")
        return self._transition

    def updateWidgets(self):
        super(ProposalTransitionCommentAddFormSQL, self).updateWidgets()
        self.widgets['transition'].mode = HIDDEN_MODE

    def updateActions(self):
        super(ProposalTransitionCommentAddFormSQL, self).updateActions()
        self.actions["save"].addClass("context")

    @button.buttonAndHandler(_(u'button_confirm', default='Confirm'),
                             name='save')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        transition = data['transition']
        comment = data.get('text')
        return self.execute_transition(transition, comment)

    @button.buttonAndHandler(_(u'button_cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ProposalTransitionCommentAddFormViewSQL(layout.FormWrapper):

    form = ProposalTransitionCommentAddFormSQL


class IProposalCommentFormSchema(Interface):
    """Schema-interface class for the proposal comment form
    """

    text = schema.Text(
        title=_('label_comment', default="Comment"),
        required=False,
        )


class ProposalCommentAddForm(form.AddForm, AutoExtensibleForm):

    fields = field.Fields(IProposalCommentFormSchema)

    @property
    def label(self):
        comment_label = translate('label_comment', domain='opengever.meeting',
                                  context=self.request)
        return u"{}: {}".format(self.context.Title().decode('utf-8'),
                                comment_label)

    def updateActions(self):
        super(ProposalCommentAddForm, self).updateActions()
        self.actions["save"].addClass("context")

    @button.buttonAndHandler(_(u'button_confirm', default='Confirm'),
                             name='save')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        comment = data.get('text')
        self.context.comment(comment)
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ProposalCommentAddFormView(layout.FormWrapper):

    form = ProposalCommentAddForm
