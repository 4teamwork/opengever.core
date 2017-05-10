from five import grok
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.keywordwidget.widget import KeywordWidget
from opengever.ogds.base.sources import AllUsersAndInboxesSourceBinder
from opengever.task import _
from opengever.task.browser.delegate import vocabulary
from opengever.task.browser.delegate.main import DelegateWizardFormMixin
from opengever.task.browser.delegate.utils import encode_data
from opengever.task.task import ITask
from plone.autoform.widgets import ParameterizedWidget
from plone.directives import form
from plone.directives.form import Form
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema


class ISelectRecipientsSchema(Schema):

    form.widget('responsibles', KeywordFieldWidget, async=True)
    responsibles = schema.List(
        title=_(u'delegate_label_responsibles', default=u'Responsibles'),
        description=_(
            u'delegate_help_responsible',
            default=u'Select one or more responsibles. For each selected '
            u'responsible a subtask will be created and assigned.'),
        required=True,
        value_type=schema.Choice(
            source=AllUsersAndInboxesSourceBinder()))

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
    fields['responsibles'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True
    )

    fields['documents'].widgetFactory = CheckBoxFieldWidget

    step_name = 'delegate_recipients'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            passed_data = data.copy()
            if passed_data['documents'] is None:
                del passed_data['documents']

            url = '%s/@@delegate_metadata?%s' % (
                self.context.absolute_url(),
                encode_data(passed_data))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        super(SelectRecipientsForm, self).updateWidgets()

        documents_source = self.fields['documents'].field.value_type.source
        if len(documents_source(self.context)) == 0:
            self.widgets['documents'].mode = HIDDEN_MODE


class SelectRecipientsStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('delegate_recipients')
    grok.require('opengever.task.AddTask')

    form = SelectRecipientsForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
