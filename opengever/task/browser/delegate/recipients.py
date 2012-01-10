from five import grok
from opengever.ogds.base import autocomplete_widget
from opengever.task import _
from opengever.task.browser.delegate import vocabulary
from opengever.task.browser.delegate.main import DelegateWizardFormMixin
from opengever.task.browser.delegate.utils import encode_data
from opengever.task.task import ITask
from plone.directives.form import Form
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from zope import schema


class ISelectRecipientsSchema(Schema):

    responsibles = schema.List(
        title=_(u'delegate_label_responsibles', default=u'Responsibles'),
        description=_(
            u'delegate_help_responsible',
            default=u'Select one or more responsibles. For each selected '
            u'responsible a subtask will be created and assigned.'),
        required=True,
        min_length=1,
        value_type=schema.Choice(
            vocabulary=u'opengever.ogds.base.AllUsersAndInboxesVocabulary'))

    documents = schema.List(
        title=_(u'delegate_label_documents', default=u'Attach documents'),
        description=_(u'Select the related documents you wish to attach '
                      u'to the new subtasks.'),
        required=False,
        value_type=schema.Choice(
            source=vocabulary.attachable_documents_vocabulary))


class SelectRecipientsForm(DelegateWizardFormMixin, Form):
    grok.context(ITask)

    fields = Fields(ISelectRecipientsSchema)
    fields['responsibles'].widgetFactory = \
        autocomplete_widget.AutocompleteMultiFieldWidget
    fields['documents'].widgetFactory = CheckBoxFieldWidget

    step_name = 'delegate_recipients'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            url = '%s/@@delegate_metadata?%s' % (
                self.context.absolute_url(),
                encode_data(data))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)


class SelectRecipientsStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('delegate_recipients')
    grok.require('opengever.task.AddTask')

    form = SelectRecipientsForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
