from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.ogds.base import autocomplete_widget
from opengever.task import _
from opengever.task.browser.delegate.main import DelegateWizardFormMixin
from opengever.task.browser.delegate.utils import create_subtasks
from opengever.task.task import ITask
from plone.directives import form
from plone.directives.form import Form
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from zope import schema
from zope.component import getMultiAdapter


class IUpdateMetadata(Schema):

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        description=_('help_title', default=u''),
        required=True)

    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
        required=True)

    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required=True)

    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required=False)


@form.default_value(field=IUpdateMetadata['title'])
def title_default(data):
    # Use the title of the task (context) as default.
    return data.context.Title()


@form.default_value(field=IUpdateMetadata['deadline'])
def deadline_default(data):
    return data.context.deadline


@form.default_value(field=IUpdateMetadata['text'])
def text_default(data):
    return data.context.text


class UpdateMetadataForm(DelegateWizardFormMixin, Form):
    grok.context(ITask)

    fields = Fields(IUpdateMetadata)
    fields['issuer'].widgetFactory = \
        autocomplete_widget.AutocompleteFieldWidget
    fields['deadline'].widgetFactory = DatePickerFieldWidget

    step_name = 'delegate_metadata'
    passed_data = ['responsibles', 'documents']

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            responsibles = self.request.get('responsibles')
            documents = self.request.get('documents')
            create_subtasks(self.context, responsibles, documents, data)
            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)

    def update(self):
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])

        super(UpdateMetadataForm, self).update()


class UpdateMetadataStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('delegate_metadata')
    grok.require('opengever.task.AddTask')

    form = UpdateMetadataForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
