"""This module is part of the accept-task wizard and provides the steps for
the "participate" method, where no successor task is created but the user
works directly in the original task.
"""

from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.task import _
from opengever.task.browser.accept.main import AcceptWizardFormMixin
from opengever.task.browser.accept.utils import accept_task_with_response
from opengever.task.task import ITask
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema


class IParticipateSchema(Schema):

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_accept_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is accepted.'),
        required=False)


class ParticipateStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IParticipateSchema)
    step_name = 'accept_participate'

    steps = (
        ('accept_choose_method',
         _(u'accept_step_1', default=u'Step 1')),

        ('accept_participate',
         _(u'accept_step_2', default=u'Step 2')),
        )

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            accept_task_with_response(self.context, data['text'])
            IStatusMessage(self.request).addStatusMessage(
                _(u'The task has been accepted.'), 'info')
            return self.request.response.redirect(self.context.absolute_url())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        url = '%s/@@accept_task' % self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)


class ParticipateStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('accept_participate')
    grok.require('cmf.AddPortalContent')

    form = ParticipateStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
