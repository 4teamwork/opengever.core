from opengever.base.browser.helper import get_css_class
from opengever.meeting import _
from opengever.meeting.browser.meetings.agendaitem import DeleteAgendaItem
from opengever.meeting.browser.meetings.agendaitem import ScheduleSubmittedProposal
from opengever.meeting.browser.meetings.agendaitem import ScheduleText
from opengever.meeting.browser.meetings.agendaitem import UpdateAgendaItemOrder
from opengever.meeting.browser.meetings.excerpt import GenerateExcerpt
from opengever.meeting.browser.meetings.protocol import DownloadGeneratedProtocol
from opengever.meeting.browser.meetings.protocol import EditProtocol
from opengever.meeting.browser.meetings.transitions import MeetingTransitionController
from opengever.meeting.browser.protocol import GenerateProtocol
from opengever.meeting.browser.protocol import UpdateProtocol
from opengever.meeting.form import ModelAddForm
from opengever.meeting.form import ModelEditForm
from opengever.meeting.model import Meeting
from plone.directives import form
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import NotFound
from zope import schema
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


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

    start = schema.Datetime(
        title=_('label_start', default=u"Start"),
        required=True)

    end = schema.Datetime(
        title=_('label_end', default=u"End"),
        required=False)


class AddMeeting(ModelAddForm):

    schema = IMeetingModel
    model_class = Meeting

    label = _('Add Meeting', default=u'Add Meeting')

    def updateWidgets(self):
        super(AddMeeting, self).updateWidgets()

        committee_id = self.context.load_model().committee_id
        self.widgets['committee'].mode = HIDDEN_MODE
        self.widgets['committee'].value = (str(committee_id), )

    def nextURL(self):
        return self._created_object.get_url()


class EditMeeting(ModelEditForm):

    fields = field.Fields(IMeetingModel)

    def __init__(self, context, request):
        super(EditMeeting, self).__init__(context, request)
        self.model = self.context.model

    def updateWidgets(self):
        super(EditMeeting, self).updateWidgets()
        self.inject_initial_data()

        committee_id = self.context.load_model().committee_id
        self.widgets['committee'].mode = HIDDEN_MODE
        self.widgets['committee'].value = (str(committee_id), )

    def nextURL(self):
        return self.model.get_url()


class MeetingView(BrowserView):

    template = ViewPageTemplateFile('templates/meeting.pt')
    implements(IBrowserView, IPublishTraverse)

    is_model_view = True
    is_model_edit_view = False

    mapped_actions = {
        'delete_agenda_item': DeleteAgendaItem,
        'download_protocol': DownloadGeneratedProtocol,
        'edit': EditMeeting,
        'generate_excerpt': GenerateExcerpt,
        'meetingtransitioncontroller': MeetingTransitionController,
        'protocol': EditProtocol,
        'schedule_proposal': ScheduleSubmittedProposal,
        'schedule_text': ScheduleText,
        'update_agenda_item_order': UpdateAgendaItemOrder,
    }

    def __init__(self, context, request):
        super(MeetingView, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        return self.template()

    def get_css_class(self, document):
        """used for display icons in the view"""
        return get_css_class(document)

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

    def url_delete_agenda_item(self, agenda_item):
        return DeleteAgendaItem.url_for(self.context, self.model, agenda_item)

    def get_protocol_document(self):
        if self.model.protocol_document:
            return self.model.protocol_document.resolve_document()

    def url_protocol(self):
        return EditProtocol.url_for(self.context, self.model)

    def url_generate_protocol(self):
        if not self.model.has_protocol_document():
            return GenerateProtocol.url_for(self.context, self.model)
        else:
            return UpdateProtocol.url_for(self.model.protocol_document)

    def url_download_protocol(self):
        return DownloadGeneratedProtocol.url_for(self.context, self.model)

    def url_manually_generate_excerpt(self):
        return GenerateExcerpt.url_for(self.context, self.model)

    def transitions(self):
        return self.model.get_state().get_transitions()

    def agenda_items(self):
        return self.model.agenda_items

    def manually_generated_excerpts(self):
        return [excerpt.resolve_document()
                for excerpt in self.model.excerpt_documents]

    @property
    def url_update_agenda_item_order(self):
        return UpdateAgendaItemOrder.url_for(self.context, self.model)

    @property
    def msg_unexpected_error(self):
        return translate(_('An unexpected error has occurred',
                           default='An unexpected error has occurred'),
                         context=self.request)
