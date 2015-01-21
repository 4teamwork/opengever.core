from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.model import create_session
from opengever.meeting import _
from opengever.meeting.browser.preprotocol import PreProtocol
from opengever.meeting.committee import ICommittee
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.service import meeting_service
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.form import AddForm
from z3c.form.form import EditForm
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


class IMeetingModel(form.Schema):
    """Meeting model schema interface."""

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        max_length=256,
        required=False)

    form.widget(date=DatePickerFieldWidget)
    date = schema.Date(
        title=_('label_date', default=u"Date"),
        required=True)

    start_time = schema.Time(
        title=_('label_start_time', default=u'Start time'),
        required=False)

    end_time = schema.Time(
        title=_('label_end_time', default=u'End time'),
        required=False)


class AddMeeting(AutoExtensibleForm, AddForm):

    ignoreContext = True
    schema = IMeetingModel

    def updateWidgets(self):
        super(AddMeeting, self).updateWidgets()

        committee_id = self.context.load_model().committee_id
        self.widgets['committee'].mode = HIDDEN_MODE
        self.widgets['committee'].value = (str(committee_id), )

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


class EditMeeting(EditForm):

    ignoreContext = True
    fields = field.Fields(IMeetingModel)

    is_model_view = True
    is_model_edit_view = True

    def __init__(self, context, request, model):
        super(EditMeeting, self).__init__(context, request)
        self.model = model
        self._has_finished_edit = False

    def inject_initial_data(self):
        if self.request.method != 'GET':
            return

        prefix = 'form.widgets.'
        values = self.model.get_edit_values(self.fields.keys())

        for fieldname, value in values.items():
            self.request[prefix + fieldname] = value

    def updateWidgets(self):
        self.inject_initial_data()
        super(EditMeeting, self).updateWidgets()

        committee_id = self.context.load_model().committee_id
        self.widgets['committee'].mode = HIDDEN_MODE
        self.widgets['committee'].value = (str(committee_id), )

    def applyChanges(self, data):
        self.model.update_model(data)
        # pretend to always change the underlying data
        self._has_finished_edit = True
        return True

    # this renames the button but otherwise preserves super's behaivor
    @button.buttonAndHandler(_('Save'), name='save')
    def handleApply(self, action):
        # self as first argument is required by the decorator
        super(EditMeeting, self).handleApply(self, action)

    def nextURL(self):
        return MeetingList.url_for(self.context, self.model)

    def render(self):
        if self._has_finished_edit:
            return self.request.response.redirect(self.nextURL())
        return super(EditMeeting, self).render()


class MeetingList(grok.View):

    implements(IPublishTraverse)
    grok.context(ICommittee)
    grok.name('meeting')

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}/{}".format(
            context.absolute_url(), cls.__view_name__, meeting.meeting_id)

    def render(self):
        """This view is never rendered directly.

        This method ist still needed to make grok checks happy, every grokked
        view must have an associated template or 'render' method.

        """
        pass

    def publishTraverse(self, request, name):
        """Allows us to handle URLs like ../committee-3/meeting/42.

        Note that meetings are stored in a relational database only and not as
        plone content.

        """
        try:
            meeting_id = int(name)
        except ValueError:
            raise NotFound

        meeting = Meeting.query.get(meeting_id)
        if meeting is None:
            raise NotFound

        return MeetingView(self.context, self.request, meeting)


class ScheduleSubmittedProposal(BrowserView):

    implements(IBrowserView)

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}".format(MeetingList.url_for(context, meeting),
                              'schedule_proposal')

    def __init__(self, context, request, meeting):
        super(ScheduleSubmittedProposal, self).__init__(context, request)
        self.meeting = meeting

    def nextURL(self):
        return MeetingList.url_for(self.context, self.meeting)

    def extract_proposal(self):
        if self.request.method != 'POST':
            return

        if 'submit' not in self.request:
            return

        proposal_value = self.request.get('proposal_id')
        try:
            proposal_id = int(proposal_value)
        except ValueError:
            return

        return meeting_service().fetch_proposal(proposal_id)

    def __call__(self):
        proposal = self.extract_proposal()
        if proposal:
            self.meeting.schedule_proposal(proposal)

        return self.request.response.redirect(self.nextURL())


class ScheduleText(ScheduleSubmittedProposal):

    implements(IBrowserView)

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}".format(MeetingList.url_for(context, meeting),
                              'schedule_text')

    def __init__(self, context, request, meeting):
        super(ScheduleSubmittedProposal, self).__init__(context, request)
        self.meeting = meeting

    def nextURL(self):
        return MeetingList.url_for(self.context, self.meeting)

    def extract_title(self):
        if self.request.method != 'POST':
            return

        if 'submit' not in self.request:
            return

        return self.request.get('title')

    def __call__(self):
        title = self.extract_title()
        if title:
            self.meeting.schedule_text(title)

        return self.request.response.redirect(self.nextURL())


class ScheduleParagraph(ScheduleText):

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}".format(MeetingList.url_for(context, meeting),
                              'schedule_paragraph')

    def __call__(self):
        title = self.extract_title()
        if title:
            self.meeting.schedule_paragraph(title)

        return self.request.response.redirect(self.nextURL())


class MeetingTransitionController(BrowserView):

    implements(IBrowserView)

    def __init__(self, context, request, model):
        super(MeetingTransitionController, self).__init__(context, request)
        self.model = model

    def __call__(self):
        transition = self.request.get('transition')
        if not self.is_valid_transition(transition):
            raise NotFound

        self.execute_transition(transition)
        return self.redirect_to_meeting()

    @classmethod
    def url_for(cls, context, meeting, transition):
        return "{}/{}?transition={}".format(
            MeetingList.url_for(context, meeting),
            'meetingtransitioncontroller',
            transition)

    def is_valid_transition(self, transition_name):
        return self.model.can_execute_transition(transition_name)

    def execute_transition(self, transition_name):
        return self.model.execute_transition(transition_name)

    def redirect_to_meeting(self):
        return self.request.RESPONSE.redirect(self.model.get_url())


class DeleteAgendaItem(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, meeting, agend_item):
        return "{}/delete_agenda_item/{}".format(
            MeetingList.url_for(context, meeting),
            agend_item.agenda_item_id)

    def __init__(self, context, request, model):
        super(DeleteAgendaItem, self).__init__(context, request)
        self.model = model
        self.item_id = None

    def nextURL(self):
        return MeetingList.url_for(self.context, self.model)

    def publishTraverse(self, request, name):
        # we only support exactly one id
        if self.item_id:
            raise NotFound
        self.item_id = name
        return self

    def __call__(self):
        if not self.item_id:
            raise NotFound

        try:
            item_id = int(self.item_id)
        except ValueError:
            raise NotFound

        agenda_item = meeting_service().fetch_agenda_item(item_id)
        if not agenda_item:
            raise NotFound

        meeting = agenda_item.meeting
        assert meeting.is_editable()

        session = create_session()
        session.delete(agenda_item)
        meeting.reorder_agenda_items()

        return self.request.response.redirect(self.nextURL())


@grok.provider(IContextSourceBinder)
def get_committee_member_vocabulary(committee):
    members = []
    for membership in committee.get_active_memberships():
        member = membership.member
        members.append(
            SimpleVocabulary.createTerm(member,
                                        str(member.member_id),
                                        member.fullname))

    return SimpleVocabulary(members)


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


class EditPreProtocol(AutoExtensibleForm, ModelEditForm, EditForm):

    ignoreContext = True
    schema = IParticipants
    content_type = Meeting

    template = ViewPageTemplateFile('pre_protocol_templates/pre_protocol.pt')

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/pre_protocol".format(MeetingList.url_for(context, meeting))

    def __init__(self, context, request, model):
        super(EditPreProtocol, self).__init__(context, request)
        self.model = model
        self._has_finished_edit = False

    def applyChanges(self, data):
        ModelEditForm.applyChanges(self, data)
        for protocol in self.get_pre_protocols():
            protocol.update(self.request)
        # pretend to always change the underlying data
        self._has_finished_edit = True
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

    # this renames the button but otherwise preserves super's behaivor
    @button.buttonAndHandler(_('Save'), name='save')
    def handleApply(self, action):
        # self as first argument is required by to the decorator
        super(EditPreProtocol, self).handleApply(self, action)

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        return self.redirect_to_meetinglist()

    def render(self):
        ModelEditForm.render(self)
        if self._has_finished_edit:
            return self.redirect_to_meetinglist()

        return self.template()

    def get_pre_protocols(self):
        for agenda_item in self.model.agenda_items:
            if not agenda_item.is_paragraph:
                yield PreProtocol(agenda_item)

    def redirect_to_meetinglist(self):
        return self.request.RESPONSE.redirect(
            MeetingList.url_for(self.context, self.model))


class MeetingView(BrowserView):

    template = ViewPageTemplateFile('meetings_templates/meeting.pt')
    implements(IBrowserView, IPublishTraverse)

    is_model_view = True
    is_model_edit_view = False

    mapped_actions = {
        'edit': EditMeeting,
        'delete_agenda_item': DeleteAgendaItem,
        'schedule_paragraph': ScheduleParagraph,
        'schedule_proposal': ScheduleSubmittedProposal,
        'schedule_text': ScheduleText,
        'pre_protocol': EditPreProtocol,
        'meetingtransitioncontroller': MeetingTransitionController,
    }

    def __init__(self, context, request, meeting):
        super(MeetingView, self).__init__(context, request)
        self.model = meeting

    def __call__(self):
        return self.template()

    def transition_url(self, transition):
        return MeetingTransitionController.url_for(
            self.context, self.model, transition.name)

    def unscheduled_proposals(self):
        return self.context.get_unscheduled_proposals()

    def publishTraverse(self, request, name):
        if name in self.mapped_actions:
            view_class = self.mapped_actions.get(name)
            return view_class(self.context, self.request, self.model)
        raise NotFound

    def url_schedule_proposal(self):
        return ScheduleSubmittedProposal.url_for(self.context, self.model)

    def url_schedule_text(self):
        return ScheduleText.url_for(self.context, self.model)

    def url_schedule_paragraph(self):
        return ScheduleParagraph.url_for(self.context, self.model)

    def url_delete_agenda_item(self, agenda_item):
        return DeleteAgendaItem.url_for(self.context, self.model, agenda_item)

    def url_pre_protocol(self):
        return EditPreProtocol.url_for(self.context, self.model)

    def transitions(self):
        return self.model.get_state().get_transitions()

    def agenda_items(self):
        return self.model.agenda_items
