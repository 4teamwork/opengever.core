from opengever.base.model import create_session
from opengever.meeting import _
from opengever.meeting.browser.meetings.meetinglist import MeetingList
from opengever.meeting.service import meeting_service
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
import json


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
        except (ValueError, TypeError):
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

        if 'schedule-paragraph' not in self.request \
                and 'schedule-text' not in self.request:
            return

        return self.request.get('title')

    def extract_is_paragraph(self):
        return 'schedule-paragraph' in self.request

    def __call__(self):
        title = self.extract_title()
        is_paragraph = self.extract_is_paragraph()
        if title:
            self.meeting.schedule_text(title, is_paragraph=is_paragraph)

        return self.request.response.redirect(self.nextURL())


class UpdateAgendaItemOrder(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, meeting):
        return "{}/{}".format(MeetingList.url_for(context, meeting),
                              'update_agenda_item_order')

    def __init__(self, context, request, model):
        super(UpdateAgendaItemOrder, self).__init__(context, request)
        self.model = model

    def __call__(self):
        data = json.loads(self.request.get('BODY'))
        new_order = [int(item_id) for item_id in data['sortOrder']]
        self.model.reorder_agenda_items(new_order)

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'messages': [{
            'messageClass': 'info',
            'messageTitle': 'Info',
            'message': _('agenda_item_order_updated',
                         default=u"Agenda Item order updated."),
        }]})


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
