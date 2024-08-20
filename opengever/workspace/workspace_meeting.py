from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.schema import UTCDatetime
from opengever.workspace import _
from opengever.workspace.interfaces import IWorkspaceMeeting
from opengever.workspace.interfaces import IWorkspaceMeetingAttendeesPresenceStateStorage
from persistent.mapping import PersistentMapping
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import provider


ATTENDEES_STATE_ABSENT = u'absent'
ATTENDEES_STATE_EXCUSED = u'excused'
ATTENDEES_STATE_PRESENT = u'present'
ALLOWED_ATTENDEES_PRESENCE_STATES = {
    ATTENDEES_STATE_ABSENT: _(u'absent', default=u'absent'),
    ATTENDEES_STATE_EXCUSED: _(u'excused', default=u'excused'),
    ATTENDEES_STATE_PRESENT: _(u'present', default=u'present')}


@provider(IFormFieldProvider)
class IWorkspaceMeetingSchema(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'responsible',
            u'start',
            u'end',
            u'location',
            u'videoconferencing_url',
        ],
    )

    form.order_after(responsible='IOpenGeverBase.description')
    responsible = schema.Choice(
        title=_('label_organizer', default='Organizer'),
        vocabulary='opengever.workspace.WorkspaceContentMembersVocabulary',
        required=True)

    chair = schema.Choice(
        title=_('label_chair', default='Chair'),
        vocabulary='opengever.workspace.WorkspaceContentMembersVocabulary',
        required=False)

    secretary = schema.Choice(
        title=_('label_secretary', default='Secretary'),
        vocabulary='opengever.workspace.WorkspaceContentMembersVocabulary',
        required=False)

    form.widget('start', DatePickerFieldWidget)
    form.order_after(start='responsible')
    start = UTCDatetime(
        title=_(u'label_start', default='Start'),
        required=True)

    form.widget('end', DatePickerFieldWidget)
    form.order_after(end='start')
    end = UTCDatetime(
        title=_(u'label_end', default='End'),
        required=False)

    form.order_after(location='end')
    location = schema.TextLine(
        title=_(u'label_location', default=u'Location'),
        required=False)

    form.order_after(videoconferencing_url='location')
    videoconferencing_url = schema.TextLine(
        title=_(u'label_video_call_link', default=u'Video Call Link'),
        required=False)

    attendees = schema.List(
        title=_(u"label_attendees", default=u"Attendees"),
        value_type=schema.Choice(
            vocabulary='opengever.workspace.WorkspaceContentMembersVocabulary',
        ),
        required=False,
        missing_value=list(),
        default=list()
    )

    form.order_after(guests='attendees')
    guests = schema.List(
        title=_(u"label_guests", default=u"Guests"),
        required=False,
        value_type=schema.TextLine(),
        default=list(),
        missing_value=list(),
    )


class WorkspaceMeeting(Container):
    implements(IWorkspaceMeeting)


@implementer(IWorkspaceMeetingAttendeesPresenceStateStorage)
@adapter(IWorkspaceMeeting)
class WorkspaceMeetingAttendeesPresenceStateStorage(object):

    ANNOTATIONS_KEY = 'opengever.workspace.meetings.attendees_presence_states'

    def __init__(self, context):
        self.context = context

    def _storage(self, create_if_missing=False):
        ann = IAnnotations(self.context)
        if self.ANNOTATIONS_KEY not in ann.keys() and create_if_missing:
            ann[self.ANNOTATIONS_KEY] = PersistentMapping()

        return ann.get(self.ANNOTATIONS_KEY, {})

    def add_or_update(self, userid, state):
        self._storage(True)[userid] = state

    def delete(self, userid):
        if self._storage().get(userid):
            del self._storage()[userid]

    def get_all(self):
        states = dict(self._storage())
        for userid in self.context.attendees:
            if userid not in states:
                states[userid] = ATTENDEES_STATE_PRESENT
        return states
