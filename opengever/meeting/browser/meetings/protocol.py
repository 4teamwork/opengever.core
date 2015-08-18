from opengever.meeting import _
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.form import ModelProxyEditForm
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.sablon import Sablon
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from plone.locking.interfaces import ILockable
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.form import EditForm
from zExceptions import Redirect
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


class DownloadGeneratedProtocol(BrowserView):

    operations = ProtocolOperations()

    def __init__(self, context, request):
        super(DownloadGeneratedProtocol, self).__init__(context, request)
        self.model = context.model

    def get_protocol_json(self, pretty=False):
        return self.operations.get_meeting_data(
            self.model).as_json(pretty=pretty)

    def __call__(self):
        sablon = Sablon(self.operations.get_sablon_template(self.model))
        sablon.process(self.get_protocol_json())

        assert sablon.is_processed_successfully(), sablon.stderr
        filename = self.operations.get_filename(self.model).encode('utf-8')
        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', MIME_DOCX)
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format(filename))
        return sablon.file_data


class DownloadProtocolJson(DownloadGeneratedProtocol):

    def __call__(self):
        response = self.request.response
        response.setHeader('X-Theme-Disabled', 'True')
        response.setHeader('Content-Type', 'application/json')
        response.setHeader("Content-Disposition",
                           'attachment; filename="{}"'.format('protocol.json'))

        return self.get_protocol_json(pretty=True)


class EditProtocol(AutoExtensibleForm, ModelProxyEditForm, EditForm):

    is_model_view = True
    is_model_edit_view = False
    ignoreContext = True
    schema = IParticipants
    content_type = Meeting

    template = ViewPageTemplateFile('templates/protocol.pt')

    def update(self):
        super(EditProtocol, self).update()

        if self.actions.executedActions:
            return
        if not self.is_available_for_current_user():
            raise Redirect(self.context.absolute_url())

        self.lock()

    def __init__(self, context, request):
        super(EditProtocol, self).__init__(context, request)
        self.model = context.model

    def is_available_for_current_user(self):
        """Check whether the current meeting can be safely unlocked.

        This means the current meeting is not locked by another user.
        """

        lockable = ILockable(self.context)
        return lockable.can_safely_unlock()

    def lock(self):
        lockable = ILockable(self.context)
        if not lockable.locked():
            lockable.lock()

    def unlock(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()

    def applyChanges(self, data):
        ModelProxyEditForm.applyChanges(self, data)
        for agenda_item in self.get_agenda_items():
            agenda_item.update(self.request)
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
        super(EditProtocol, self).handleApply(self, action)
        api.portal.show_message(
            _(u'message_changes_saved', default='Changes saved'),
            self.request)

        self.unlock()
        return self.redirect_to_meeting()

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.unlock()
        return self.redirect_to_meeting()

    def render(self):
        ModelProxyEditForm.render(self)
        return self.template()

    def get_agenda_items(self):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.is_paragraph:
                yield agenda_item

    def redirect_to_meeting(self):
        return self.request.RESPONSE.redirect(self.model.get_url())
