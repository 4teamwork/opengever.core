from opengever.meeting import _
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.browser.preprotocol import PreProtocol
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.form import EditForm
from zope import schema


class IParticipants(form.Schema):
    """Schema interface for participants of a meeting."""

    presidency = schema.Choice(
        title=_('label_presidency', default=u'Presidency'),
        source=get_committee_member_vocabulary,
        required=False)

    secretary = schema.Choice(
        title=_('label_secretary', default=u'Secretary'),
        source=get_committee_member_vocabulary,
        required=False)

    form.widget(participants=CheckBoxFieldWidget)
    participants = schema.List(
        title=_('label_participants', default='Participants'),
        value_type=schema.Choice(
            source=get_committee_member_vocabulary,
        ),
        required=False,
    )

    other_participants = schema.Text(
        title=_(u"label_other_participants", default=u"Other Participants"),
        required=False)


class EditPreProtocol(AutoExtensibleForm, ModelProxyEditForm, EditForm):

    ignoreContext = True
    schema = IParticipants
    content_type = Meeting

    template = ViewPageTemplateFile('templates/pre_protocol.pt')

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/pre_protocol".format(MeetingList.url_for(context, meeting))

    def __init__(self, context, request, model):
        super(EditPreProtocol, self).__init__(context, request)
        self.model = model

    def applyChanges(self, data):
        ModelProxyEditForm.applyChanges(self, data)
        for protocol in self.get_pre_protocols():
            protocol.update(self.request)
        # pretend to always change the underlying data
        return True

    def partition_data(self, data):
        participation_data = {}
        for key in self.schema.names():
            if key in data:
                participation_data[key] = data.pop(key)
        return {}, participation_data

    def _convert_value(self, value):
        if isinstance(value, Member):
            value = str(value.member_id)
        elif isinstance(value, list):
            value = [self._convert_value(item) for item in value]
        return value

    def get_edit_values(self, keys):
        values = {}
        for fieldname in keys:
            value = getattr(self.model, fieldname, None)
            if value is None:
                continue
            values[fieldname] = self._convert_value(value)
        return values

    def update_model(self, model_data):
        self.model.update_model(model_data)

    # this renames the button but otherwise preserves super's behaviour
    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        # self as first argument is required by to the decorator
        super(EditPreProtocol, self).handleApply(self, action)
        api.portal.show_message(
            _(u'message_changes_saved', default='Changes saved'),
            self.request)
        return self.redirect_to_meetinglist()

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meetinglist()

    def render(self):
        ModelProxyEditForm.render(self)
        return self.template()

    def get_pre_protocols(self):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.is_paragraph:
                yield PreProtocol(agenda_item)

    def redirect_to_meetinglist(self):
        return self.request.RESPONSE.redirect(
            MeetingList.url_for(self.context, self.model))
