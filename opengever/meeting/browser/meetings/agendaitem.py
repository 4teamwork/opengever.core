from opengever.base.response import JSONResponse
from opengever.meeting import _
from opengever.meeting.service import meeting_service
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class ScheduleSubmittedProposal(BrowserView):

    implements(IBrowserView)

    @classmethod
    def url_for(cls, context, meeting):
        return meeting.get_url(view='schedule_proposal')

    def __init__(self, context, request):
        super(ScheduleSubmittedProposal, self).__init__(context, request)
        self.meeting = self.context.model

    def nextURL(self):
        return self.meeting.get_url()

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
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")

        proposal = self.extract_proposal()
        if proposal:
            self.meeting.schedule_proposal(proposal)

        return self.request.response.redirect(self.nextURL())


class ScheduleText(ScheduleSubmittedProposal):

    implements(IBrowserView)

    @classmethod
    def url_for(cls, context, meeting):
        return meeting.get_url(view='schedule_text')

    def nextURL(self):
        return self.meeting.get_url()

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
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")

        title = self.extract_title()
        is_paragraph = self.extract_is_paragraph()
        if title:
            self.meeting.schedule_text(title, is_paragraph=is_paragraph)

        return self.request.response.redirect(self.nextURL())


class UpdateAgendaItemOrder(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, meeting):
        return meeting.get_url(view='update_agenda_item_order')

    def __init__(self, context, request):
        super(UpdateAgendaItemOrder, self).__init__(context, request)
        self.model = self.context.model

    def __call__(self):
        if not self.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        new_order = [int(item_id) for item_id in self.request.get('sortOrder[]')]
        self.model.reorder_agenda_items(new_order)

        numbers = dict((each.agenda_item_id, each.number) for each in
                       self.model.agenda_items)

        return JSONResponse(self.request).info(_('agenda_item_order_updated',
                                        default=u"Agenda Item order updated.")).data(numbers=numbers).dump()

    def update_sortorder(self, json_data):
        new_order = [int(item_id) for item_id in json_data['sortOrder']]
        self.model.reorder_agenda_items(new_order)

        numbers = dict((each.agenda_item_id, each.number) for each in
                       self.model.agenda_items)

        return JSONResponse(self.request).info(_('agenda_item_order_updated',
                                        default=u"Agenda Item order updated.")).data(numbers=numbers).dump()


class DeleteAgendaItem(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, meeting, agend_item):

        return "{}/{}".format(
            meeting.get_url('delete_agenda_item'),
            agend_item.agenda_item_id)

    def __init__(self, context, request):
        super(DeleteAgendaItem, self).__init__(context, request)
        self.model = self.context.model
        self.item_id = None

    def nextURL(self):
        return self.model.get_url()

    def publishTraverse(self, request, name):
        # we only support exactly one id
        if self.item_id:
            raise NotFound
        self.item_id = name
        return self

    def __call__(self):
        if not self.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        if not self.item_id:
            raise NotFound

        try:
            item_id = int(self.item_id)
        except ValueError:
            raise NotFound

        agenda_item = meeting_service().fetch_agenda_item(item_id)
        if not agenda_item:
            raise NotFound

        agenda_item.remove()

        return self.request.response.redirect(self.nextURL())


class UpdateAgendaItem(BrowserView):

    @classmethod
    def url_for(cls, context, meeting):
        return meeting.get_url(view='update_agenda_item')

    def __call__(self):
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        title = self.request.get('title')
        agenda_item_id = self.request.get('agenda_item_id')
        if not title or not agenda_item_id:
            return JSONResponse(self.request).error(_('agenda_item_update_empty_string',
                                                   default=u"Agenda Item title must not be empty.")).remain().dump()

        agenda_item = meeting_service().fetch_agenda_item(agenda_item_id)
        if not agenda_item:
            raise NotFound

        agenda_item.set_title(title)
        return JSONResponse(self.request).info(_('agenda_item_updated',
                                               default=u"Agenda Item updated.")).proceed().dump()
