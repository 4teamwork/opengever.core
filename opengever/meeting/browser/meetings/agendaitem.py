from opengever.base.browser.helper import get_css_class
from opengever.base.response import JSONResponse
from opengever.meeting import _
from opengever.meeting.service import meeting_service
from plone import api
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
import json
import transaction


class IAgendaItemActions(Interface):

    def list():
        """Returns json list of all agendaitems for the current
        context (meeting).
        """

    def edit():
        """Updates the title fo the current agendaitem, with the one given by
        the request parameter `title`. The view expect that its called by
        traversing over the agendaitem: `plone/meeting-3/14/edit` for example.
        """

    def delete():
        """Remove or unschedule (proposal related) the current agendaitem.
        The view expect that its called by traversing over the agendaitem:
        `plone/meeting-3/14/delete` for example.
        """

    def update_order():
        """Updates the order of the meetings agendaitems. The new sortOrder
        is expected in the request parameter `sortOrder` and should be a list
        of agendaitem ids.
        """

    def schedule_text():
        """Schedule the given Text (request parameter `title`) for the current
        meeting.
        """

    def schedule_paragraph():
        """Schedule the given Paragraph (request parameter `title`) for the
        current meeting.
        """

    def decide():
        """Decide the current agendaitem and decide the meeting.
        """


class AgendaItemsView(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    def publishTraverse(self, request, name):
        if name in IAgendaItemActions.names():
            return getattr(self, name)

        # we only support exactly one id
        if self.agenda_item_id:
            raise NotFound
        self.agenda_item_id = int(name)
        return self

    def __init__(self, context, request):
        super(AgendaItemsView, self).__init__(context, request)
        self.meeting = self.context.model
        self.agenda_item_id = None

    def _serialize_submitted_documents(self, item):
        if not item.has_proposal:
            return []

        return map(lambda document: {
            'title': document.title,
            'link': document.absolute_url(),
            'css_class': get_css_class(document)},
            item.proposal.resolve_submitted_documents())

    def _serialize_submitted_excerpt(self, item):
        if not item.has_proposal:
            return None

        excerpt = item.proposal.resolve_submitted_excerpt_document()
        if excerpt is None:
            return {}

        return {
            'title': excerpt.title,
            'link': excerpt.absolute_url(),
            'css_class': get_css_class(excerpt),
            }

    def has_documents(self, item):
        if not item.has_proposal:
            return False

        return bool(item.proposal.submitted_documents or
                item.proposal.submitted_excerpt_document)

    def list(self):
        """Returns json list of all agendaitems for the current
        context (meeting).
        """
        meeting = self.context.model
        agenda_items = []
        for item in meeting.agenda_items:
            data = item.serialize()
            data['documents'] = self._serialize_submitted_documents(item)
            data['excerpt'] = self._serialize_submitted_excerpt(item)
            data['has_documents'] = self.has_documents(item)
            data['delete_link'] = meeting.get_url(
                view='agenda_items/{}/delete'.format(item.agenda_item_id))
            data['edit_link'] = meeting.get_url(
                view='agenda_items/{}/edit'.format(item.agenda_item_id))
            if item.is_decide_possible():
                data['decide_link'] = meeting.get_url(
                    view='agenda_items/{}/decide'.format(item.agenda_item_id))

            agenda_items.append(data)

        return JSONResponse(self.request).data(items=agenda_items).dump()

    def update_order(self):
        """Updates the order of the agendaitems. The new sortOrder is expected
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

        return JSONResponse(self.request).info(
            _(u'agenda_item_deleted',
              default=u'Agenda Item Successfully deleted')).dump()

    def decide(self):
        """Decide the current agendaitem and move the meeting in the
        held state.
        """
        meeting_state = self.meeting.get_state()

        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        agenda_item = meeting_service().fetch_agenda_item(self.agenda_item_id)
        if not agenda_item:
            raise NotFound

        agenda_item.decide()

        response = JSONResponse(self.request)
        if agenda_item.has_proposal:
            response.info(
                _(u'agenda_item_proposal_decided',
                  default=u'Agenda Item decided and excerpt generated.'))
        else:
            response.info(_(u'agenda_item_decided',
                            default=u'Agenda Item decided.'))

        if meeting_state != self.meeting.get_state():
            response.redirect(self.context.absolute_url())
            msg = _(u'agenda_item_meeting_held',
                default=u"Agendaitem has been decided and the meeting has been held.")
            api.portal.show_message(message=msg, request=self.request, type='info')

        return response.dump()

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
