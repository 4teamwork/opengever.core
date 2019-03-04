from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.keywordwidget.widget import KeywordWidget
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.task import _
from opengever.task.browser.delegate import vocabulary
from opengever.task.browser.delegate.main import DelegateWizardFormMixin
from opengever.task.browser.delegate.utils import encode_data
from plone.autoform.widgets import ParameterizedWidget
from plone.autoform import directives as form
from z3c.form.form import Form
from plone.supermodel.model import Schema
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
        missing_value=[],
        value_type=schema.Choice(
            source=AllUsersInboxesAndTeamsSourceBinder()))

    documents = schema.List(
        title=_(u'delegate_label_documents', default=u'Attach documents'),
        description=_(u'Select the related documents you wish to attach '
                      u'to the new subtasks.'),
        missing_value=[],
        required=False,
        value_type=schema.Choice(
            source=vocabulary.attachable_documents_vocabulary))


class SelectRecipientsForm(DelegateWizardFormMixin, Form):

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


class SelectRecipientsStepView(FormWrapper):

    form = SelectRecipientsForm
