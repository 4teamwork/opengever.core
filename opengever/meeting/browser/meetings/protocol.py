from calendar import timegm
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.date_time import as_utc
from opengever.base.response import JSONResponse
from opengever.base.schema import UTCDatetime
from opengever.meeting import _
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.command import ProtocolOperations
from opengever.meeting.model import Meeting
from opengever.meeting.sablon import Sablon
from opengever.meeting.vocabulary import get_committee_member_vocabulary
from opengever.ogds.base.actor import Actor
from plone import api
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

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True)

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

    form.widget('start', DatePickerFieldWidget)
    start = UTCDatetime(
        title=_('label_start', default=u"Start"),
        required=True)

    form.widget('end', DatePickerFieldWidget)
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


class EditProtocol(ModelEditForm):

    has_model_breadcrumbs = True
    ignoreContext = True
    schema = IMeetingMetadata
    content_type = Meeting
    enable_unload_protection = False

    agenda_item_fields = [
        {"name": "legal_basis",
         "label": _("label_legal_basis", default="Legal basis"),
         "needs_proposal": True},
        {"name": "initial_position",
         "label": _("label_initial_position", default="Initial position"),
         "needs_proposal": True},
        {"name": "proposed_action",
         "label": _("label_proposed_action", default="Proposed action"),
         "needs_proposal": True},
        {"name": "considerations",
         "label": _("label_considerations", default="Considerations"),
         "needs_proposal": True},
        {"name": "discussion",
         "label": _("label_discussion", default="Discussion"),
         "needs_proposal": False},
        {"name": "decision",
         "label": _("label_decision", default="Decision"),
         "needs_proposal": False},
        {"name": "publish_in",
         "label": _("label_publish_in", default="Publish in"),
         "needs_proposal": True},
        {"name": "disclose_to",
         "label": _("label_disclose_to", default="Disclose to"),
         "needs_proposal": True},
        {"name": "copy_for_attention",
         "label": _("label_copy_for_attention", default="Copy for attention"),
         "needs_proposal": True},
    ]

    template = ViewPageTemplateFile('templates/protocol.pt')

    def __init__(self, context, request):
        """
        Introduce ```_has_successfully_saved``` because we have two diffrent response types.
        If the protocol has been saved we want to return a JSON response.
        """
        super(EditProtocol, self).__init__(context, request, context.model)
        self._has_write_conflict = False
        self._is_locked_by_another_user = False
        self._has_successfully_saved = False

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
        self._has_successfully_saved = True

        self.unlock()
        # pretend to always change the underlying data
        return True

    # needs duplication, otherwise button does not appear
    @button.buttonAndHandler(_('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        """"""
        if self.has_write_conflict():
            self._has_write_conflict = True
            return
        if self.is_locked_by_another_user():
            self._is_locked_by_another_user = True
            return

        super(EditProtocol, self).handleApply(self, action)

    def has_write_conflict(self):
        return self.server_timestamp != self.client_timestamp

    def is_locked_by_another_user(self):
        """Return False if the document is locked by the current user or is
        not locked at all, True otherwise.

        """
        lockable = ILockable(self.context)
        return not lockable.can_safely_unlock()

    def get_lock_creator_user_name(self):
        lockable = ILockable(self.context)
        creator = lockable.lock_info()[0]['creator']
        return Actor.lookup(creator).get_label()

    def redirect_to_next_url(self):
        """
        We dont want to make a redirect here because this view will be called
        asynchronously.
        """
        pass

    @button.buttonAndHandler(_('label_close', default=u'Close'), name='cancel')
    def cancel(self, action):
        self.unlock()
        # self as first argument is required by to the decorator
        super(EditProtocol, self).cancel(self, action)

    def render(self):
        if self._has_write_conflict:
            msg = _(u'message_write_conflict',
                    default='Your changes were not saved, the protocol has '
                            'been modified in the meantime.')
            return JSONResponse(self.request).data(hasConflict=True).dump()

        elif self._is_locked_by_another_user:
            msg = _(u'message_locked_by_another_user',
                    default='Your changes were not saved, the protocol is '
                            'locked by ${username}.',
                    mapping={'username': self.get_lock_creator_user_name()})
            return JSONResponse(self.request).error(msg).dump()

        elif self._has_successfully_saved:
            api.portal.show_message(
                _(u'message_changes_saved', default='Changes saved'),
                self.request)
            return JSONResponse(self.request).redirect(self.nextURL()).dump()

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

    def is_field_visible(self, field, agenda_item):
        field_value = getattr(agenda_item, field.get('name'))
        if agenda_item.is_decided() and not field_value:
            return False

        if field['needs_proposal']:
            return agenda_item.has_proposal
        else:
            return not agenda_item.is_paragraph

    @property
    def server_timestamp(self):
        """Return the modified timestamp as seconds since the epoch."""

        return timegm(as_utc(self.model.modified).timetuple())

    @property
    def client_timestamp(self):
        """Return the modified timestamp that has been submitted by the
        client.

        """
        timestamp = self.request.get('modified')
        if not timestamp:
            return None

        return int(timestamp)
