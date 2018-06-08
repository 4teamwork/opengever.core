from opengever.meeting import _
from opengever.meeting.browser.proposaltransitions import ProposalTransitionController
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import layout
from Products.CMFPlone import PloneMessageFactory as PMF
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser import radio
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import BadRequest
from zope import schema
from zope.interface import Interface
from zope.interface import provider
from zope.i18n import translate
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def getTransitionVocab(context):
    transitions = []
    for transition in context.get_transitions():
        transitions.append(SimpleVocabulary.createTerm(
            transition.name,
            transition.name,
            PMF(transition.name, default=transition.title)))

    return SimpleVocabulary(transitions)


class IProposalTransitionCommentFormSchema(Interface):
    """Schema-interface class for the proposal transition comment form
    """
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        source=getTransitionVocab,
        required=False,
        )

    text = schema.Text(
        title=_('label_comment', default="Comment"),
        required=False,
        )


class ProposalTransitionCommentAddForm(form.AddForm, AutoExtensibleForm):

    allow_prefill_from_GET_request = True  # XXX

    fields = field.Fields(IProposalTransitionCommentFormSchema)
    # keep widget for converters (even though field is hidden)
    fields['transition'].widgetFactory = radio.RadioFieldWidget

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
        form.AddForm.updateWidgets(self)
        self.widgets['transition'].mode = HIDDEN_MODE

    def updateActions(self):
        super(ProposalTransitionCommentAddForm, self).updateActions()
        self.actions["save"].addClass("context")

    @button.buttonAndHandler(_(u'button_confirm', default='Confirm'),
                             name='save')
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            errorMessage = '<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage
            return None

        else:
            transition = data['transition']
            comment = data.get('text')
            controller = ProposalTransitionController(self.context, self.request)
            return controller.execute_transition(transition, comment)

    @button.buttonAndHandler(_(u'button_cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ProposalTransitionCommentAddFormView(layout.FormWrapper):

    form = ProposalTransitionCommentAddForm


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
            errorMessage = '<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage
            return None

        else:
            comment = data.get('text')
            self.context.comment(comment)
            return self.request.RESPONSE.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ProposalCommentAddFormView(layout.FormWrapper):

    form = ProposalCommentAddForm
