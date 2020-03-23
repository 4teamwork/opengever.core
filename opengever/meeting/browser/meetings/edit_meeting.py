from calendar import timegm
from opengever.base import _ as _base
from opengever.base.browser.modelforms import ModelEditForm
from opengever.base.date_time import as_utc
from opengever.meeting import _
from opengever.meeting.browser.meetings.protocol import IMeetingMetadata
from opengever.meeting.model import Meeting
from opengever.ogds.base.actor import Actor
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.user import User
from plone.locking.interfaces import ILockable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.interfaces import IDataConverter
from zExceptions import Redirect


class EditMeetingView(ModelEditForm):
    """The edit meeting view provides a form for editing the meeting details.

    This view is used when the word meeting feature is enabled.
    The older implementation used the protocol view for editing these fields.
    This view was copied from the protocol view.
    """

    ignoreContext = True
    schema = IMeetingMetadata
    content_type = Meeting
    enable_unload_protection = False
    template = ViewPageTemplateFile('templates/edit_meeting.pt')

    def __init__(self, context, request):
        """
        Introduce ```_has_successfully_saved``` because we have two different
        response types.
        If the protocol has been saved we want to return a JSON response.
        """
        super(EditMeetingView, self).__init__(context, request, context.model)
        self._has_write_conflict = False
        self._is_locked_by_another_user = False
        self._has_successfully_saved = False

    def action_visible(self):
        """Returns ``True`` when the "Edit" action should be visible.
        """
        return self.model.is_editable()

    def update(self):
        super(EditMeetingView, self).update()
        if self.actions.executedActions:
            return

    def updateFields(self):
        super(EditMeetingView, self).updateFields()
        self.fields = (self.fields.omit('presidency')
                       .omit('participants'))

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        values = self.model.get_edit_values(self.fields.keys())
        # XXX - Doing this instead of a data adapter
        secretary = values.get('secretary')
        if secretary:
            if isinstance(secretary, User):
                values['secretary'] = secretary.userid

        for fieldname, value in values.items():
            widget = self.widgets[fieldname]
            value = IDataConverter(widget).toWidgetValue(value)
            widget.value = value

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
        # XXX - Doing this instead of a data adapter
        secretary = data.get('secretary')
        if secretary:
            # We get in the user id from the keyword widget
            ogds_user = ogds_service().fetch_user(secretary)
            if ogds_user:
                data['secretary'] = ogds_user

        ModelEditForm.applyChanges(self, data)
        self.unlock()
        return True

    # needs duplication, otherwise button does not appear
    @button.buttonAndHandler(_base('Save', default=u'Save'), name='save')
    def handleApply(self, action):
        """"""
        if self.has_write_conflict():
            self.status = _(u'message_write_conflict',
                            default='Your changes were not saved, the protocol has '
                            'been modified in the meantime.')
            return
        if self.is_locked_by_another_user():
            self.status = _(u'message_locked_by_another_user',
                            default='Your changes were not saved, the protocol is '
                            'locked by ${username}.',
                            mapping={'username': self.get_lock_creator_user_name()})
            return

        super(EditMeetingView, self).handleApply(self, action)

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

    @button.buttonAndHandler(_base(u'label_cancel', default=u'Cancel'), name='cancel')
    def cancel(self, action):
        self.unlock()
        # self as first argument is required by to the decorator
        super(EditMeetingView, self).cancel(self, action)

    def render(self):
        if not self.is_available_for_current_user():
            raise Redirect(self.context.absolute_url())

        self.lock()
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
