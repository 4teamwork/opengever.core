from opengever.base.response import JSONResponse
from opengever.meeting import _
from opengever.meeting.service import meeting_service
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
import json
from opengever.base.browser.helper import get_css_class


class ScheduleSubmittedProposal(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    @classmethod
    def url_for(cls, context, meeting, proposal):
        return '{}/{}'.format(
            meeting.get_url(view='schedule_proposal'),
            proposal.proposal_id)

    def __init__(self, context, request):
        super(ScheduleSubmittedProposal, self).__init__(context, request)
        self.meeting = self.context.model
        self.proposal_id = None

    def publishTraverse(self, request, name):
        # we only support exactly one id
        if self.proposal_id:
            raise NotFound
        self.proposal_id = int(name)
        return self

    def extract_proposal(self):
        return meeting_service().fetch_proposal(self.proposal_id)

    def __call__(self):
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")

        proposal = self.extract_proposal()
        if proposal:
            self.meeting.schedule_proposal(proposal)

        return JSONResponse(self.request).info(
            _('Scheduled Successfully')).proceed().dump()


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

        self.model.reorder_agenda_items(json.loads(self.request.get('sortOrder')))

        return JSONResponse(self.request).info(_('agenda_item_order_updated',
                                        default=u"Agenda Item order updated.")).dump()

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

        return JSONResponse(self.request).info("Successfully deleted").dump()


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


class AgendaItemsView(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    def __init__(self, context, request):
        super(AgendaItemsView, self).__init__(context, request)
        self.meeting = self.context.model
        self.agenda_item_id = None

    def _serialize_submitted_documents(self, item):
        if not item.has_proposal:
            return []

        return map(lambda document : {
            'title': document.title,
            'link': document.absolute_url(),
            'css_class': get_css_class(document)},
            item.proposal.resolve_submitted_documents())

    def _serialize_submitted_excerpt(self, item):
        if not item.has_proposal:
            return None

        excerpt = item.proposal.resolve_submitted_excerpt_document(),
        return {
            'title': excerpt.title,
            'link': excerpt.absolute_url(),
            'css_class': get_css_class(excerpt),
            }

    def publishTraverse(self, request, name):
        if name == 'list':
            return self.list

        if name == 'edit':
            return self.edit

        if name == 'delete':
            return self.delete

        if name == 'update_order':
            return self.update_order

        if name == 'schedule_text':
            return self.schedule_text

        if name == 'schedule_paragraph':
            return self.schedule_paragraph

        # we only support exactly one id
        if self.agenda_item_id:
            raise NotFound
        self.agenda_item_id = int(name)
        return self

    def list(self):
        """
        Returns json list of all agendaitems for the current context (meeting).
        """
        meeting = self.context.model
        agenda_items = []
        for item in meeting.agenda_items:
            data = item.serialize()
            data['documents'] = self._serialize_submitted_documents(item)
            data['excerpt'] = self._serialize_submitted_documents(item)
            data['delete_link'] = meeting.get_url(
                view='agenda_items/{}/delete'.format(item.agenda_item_id))
            data['edit_link'] = meeting.get_url(
                view='agenda_items/{}/edit'.format(item.agenda_item_id))
            agenda_items.append(data)

        return JSONResponse(self.request).data(items=agenda_items).dump()

    def update_order(self):
        """Updat the order of the agendaitems. The new sortOrder is expected
        in the request parameter `sortOrder`.
        """
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        self.context.model.reorder_agenda_items(
            json.loads(self.request.get('sortOrder')))

        return JSONResponse(self.request).info(
            _('agenda_item_order_updated',
              default=u"Agenda Item order updated.")).dump()

    def edit(self):
        """Updates the title of the agendaitem, with the one given by the
        request parameter `title`.
        """
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        agenda_item = meeting_service().fetch_agenda_item(self.agenda_item_id)
        if not agenda_item:
            raise NotFound

        title = self.request.get('title')
        if not title:
            return JSONResponse(self.request).error(
                _('agenda_item_update_empty_string',
                  default=u"Agenda Item title must not be empty.")).remain().dump()

        agenda_item.set_title(title)
        return JSONResponse(self.request).info(
            _('agenda_item_updated',
              default=u"Agenda Item updated.")).proceed().dump()

    def delete(self):
        """Unschedule the current agenda_item. If the agenda_item has no
        proposal, the agenda_item gets deleted. If there is a proposal related,
        the proposal is unscheduled.
        """

        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        agenda_item = meeting_service().fetch_agenda_item(self.agenda_item_id)
        if not agenda_item:
            raise NotFound

        agenda_item.remove()

        return JSONResponse(self.request).info("Successfully deleted").dump()

    def schedule_paragraph(self):
        """Schedule the given Paragraph (request parameter `title`) for the current
        meeting.
        """
        self.check_editable()

        title = self.request.get('title')
        if not title:
            raise ValueError

        self.meeting.schedule_text(title, is_paragraph=True)
        return JSONResponse(self.request).info(
            _('paragraph_added', default=u"Paragrap successfully added.")
        ).proceed().dump()

    def schedule_text(self):
        """Schedule the given Text (request parameter `title`) for the current
        meeting.
        """
        self.check_editable()
        title = self.request.get('title')
        if not title:
            raise ValueError

        self.meeting.schedule_text(title)
        return JSONResponse(self.request).info(
            _('text_added', default=u"Texst successfully added.")).proceed().dump()

    def check_editable(self):
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")
