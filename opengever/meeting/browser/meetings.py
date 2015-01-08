from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.core.model import create_session
from opengever.meeting import _
from opengever.meeting.committee import ICommittee
from opengever.meeting.model import Meeting
from opengever.meeting.service import meeting_service
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import field
from z3c.form.form import AddForm
from z3c.form.form import EditForm
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import NotFound
from zope import schema
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class IMeetingModel(form.Schema):
    """Proposal model schema interface."""

    committee = schema.Choice(
        title=_('label_committee', default=u'Committee'),
        source='opengever.meeting.CommitteeVocabulary',
        required=True)

    location = schema.TextLine(
        title=_(u"label_location", default=u"Location"),
        description=_('help_location', default=u""),
        max_length=256,
        required=False)

    form.widget(date=DatePickerFieldWidget)
    date = schema.Date(
        title=_('label_date', default=u"Date"),
        description=_("help_date", default=u""),
        required=True)

    start_time = schema.Time(
        title=_('label_start_time', default=u'Start time'),
        description=_("help_start_time", default=u""),
        required=False)

    end_time = schema.Time(
        title=_('label_end_time', default=u'End time'),
        description=_("help_end_time", default=u""),
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
        # self as first argument is required by to the decorator
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
        return "{}/{}/{}".format(
            MeetingList.url_for(context, meeting),
            'delete_agenda_item',
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

    def transitions(self):
        return self.model.get_state().get_transitions()

    def agenda_items(self):
        return self.model.agenda_items
