from opengever.base.schema import UTCDatetime
from opengever.meeting import _
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Meeting
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
from zExceptions import Redirect
from zope import schema


class IMeetingMetadata(form.Schema):
    """Schema interface for meeting metadata."""

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

    protocol_start_page_number = schema.Int(
        title=_(u"label_protocol_start_page_number",
                default=u"Protocol start-page"),
        required=False
    )

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        max_length=256,
        required=False)

    start = UTCDatetime(
        title=_('label_start', default=u"Start"),
        required=True)

    end = UTCDatetime(
        title=_('label_end', default=u"End"),
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


class EditProtocol(AutoExtensibleForm, ModelEditForm):

    has_model_breadcrumbs = True
    ignoreContext = True
    schema = IMeetingMetadata
    content_type = Meeting

    template = ViewPageTemplateFile('templates/protocol.pt')

    def __init__(self, context, request):
        super(EditProtocol, self).__init__(context, request, context.model)

    def update(self):
        super(EditProtocol, self).update()

        if self.actions.executedActions:
            return
        if not self.is_available_for_current_user():
            raise Redirect(self.context.absolute_url())

        self.lock()

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
        ModelEditForm.applyChanges(self, data)

        for agenda_item in self.get_agenda_items():
            agenda_item.update(self.request)

        api.portal.show_message(
            _(u'message_changes_saved', default='Changes saved'),
            self.request)

        self.unlock()
        # pretend to always change the underlying data
        return True

    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        # needs duplication, otherwise button does not appear
        super(EditProtocol, self).handleApply(self, action)

    @button.buttonAndHandler(_('Cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        self.unlock()
        # self as first argument is required by to the decorator
        super(EditProtocol, self).cancel(self, action)

    def render(self):
        return self.template()

    def get_agenda_items(self, include_paragraphs=False):
        for agenda_item in self.model.agenda_items:
            if agenda_item.is_paragraph:
                if include_paragraphs:
                    yield agenda_item
            else:
                yield agenda_item

    def nextURL(self):
        return self.model.get_url()
