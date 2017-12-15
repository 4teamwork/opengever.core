from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.widget import KeywordWidget
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from opengever.task import _
from opengever.task.browser.delegate.main import DelegateWizardFormMixin
from opengever.task.browser.delegate.utils import create_subtasks
from plone import api
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel.model import Schema
from plone.z3cform.layout import FormWrapper
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def title_default(context):
    # Use the title of the task (context) as default.
    return context.title


@provider(IContextAwareDefaultFactory)
def deadline_default(context):
    return context.deadline


@provider(IContextAwareDefaultFactory)
def text_default(context):
    return context.text


class IUpdateMetadata(Schema):

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        description=_('help_title', default=u''),
        defaultFactory=title_default,
        required=True)

    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        source=UsersContactsInboxesSourceBinder(),
        required=True)

    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        defaultFactory=deadline_default,
        required=True)

    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        defaultFactory=text_default,
        required=False)


class UpdateMetadataForm(DelegateWizardFormMixin, Form):
    fields = Fields(IUpdateMetadata)
    fields['issuer'].widgetFactory = ParameterizedWidget(
        KeywordWidget,
        async=True
    )
    fields['deadline'].widgetFactory = DatePickerFieldWidget

    step_name = 'delegate_metadata'
    passed_data = ['responsibles', 'documents']

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_save(self, action):
        data, errors = self.extractData()
        if not errors:
            responsibles = self.request.get('responsibles')
            documents = self.request.get('documents', None) or []
            subtasks = create_subtasks(self.context, responsibles,
                                       documents, data)

            msg = _(u'${subtask_num} subtasks were create.',
                    mapping={u'subtask_num': len(subtasks)})
            IStatusMessage(self.request).addStatusMessage(msg, 'info')

            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        super(UpdateMetadataForm, self).updateWidgets()
        self.widgets['issuer'].value = [api.user.get_current().getId()]


class UpdateMetadataStepView(FormWrapper):

    form = UpdateMetadataForm
