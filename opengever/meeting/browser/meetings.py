from five import grok
from opengever.core.model import create_session
from opengever.meeting import _
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Meeting
from Products.Five.browser import BrowserView
from z3c.form import field
from z3c.form.form import AddForm
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMeetingModel(Interface):
    """Proposal model schema interface."""

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        description=_('help_location', default=u""),
        max_length=256,
        required=False,
        )

    date = schema.Date(
        title=_('label_date', default=u"Date"),
        description=_("help_date", default=u""),
        required=True,
        )

    start_time = schema.Time(
        title=_('label_start_time', default=u'Start time'),
        description=_("help_start_time", default=u""),
        required=False)

    end_time = schema.Time(
        title=_('label_end_time', default=u'End time'),
        description=_("help_end_time", default=u""),
        required=False)


class AddMeeting(AddForm):

    ignoreContext = True
    fields = field.Fields(IMeetingModel)

    def __init__(self, context, request):
        super(AddMeeting, self).__init__(context, request)
        self._created_object = None

    def create(self, data):
        return Meeting(**data)

    def add(self, obj):
        session = create_session()
        session.add(obj)
        session.flush()  # required to create an autoincremented id
        self._created_object = obj

    def nextURL(self):
        return MeetingList.url_for(self.context, self._created_object)


class MeetingList(grok.View):

    implements(IPublishTraverse)
    grok.context(ICommittee)
    grok.name('meeting')

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/@@{}/{}".format(
            context.absolute_url(), cls.__view_name__, meeting.meeting_id)

    def render(self):
        """This view is never rendered directly.

        This method ist still needed to make grok checks happy, every grokked
        view must have an associated template or 'render' method.

        """
        pass

    def publishTraverse(self, request, name):
        """
        """
        try:
            meeting_id = int(name)
        except ValueError:
            raise NotFound

        meeting = Meeting.query.get(meeting_id)
        if meeting is None:
            raise NotFound

        return MeetingView(self.context, self.request, meeting)


class EditMeetingView(BrowserView):

    def __init__(self, context, request):
        super(EditMeetingView, self).__init__(context, request)

    def __call__(self):
        return 'edit'


class MeetingView(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    mapped_actions = {
        'edit': EditMeetingView
    }

    def __init__(self, context, request, meeting):
        super(MeetingView, self).__init__(context, request)
        self.meeting = meeting

    def __call__(self):
        return self.meeting

    def publishTraverse(self, request, name):
        if name in self.mapped_actions:
            return self.mapped_actions.get(name)(self.context, self.request)
        raise NotFound
