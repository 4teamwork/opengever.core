from opengever.base.response import JSONResponse
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting import _
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting import require_word_meeting_feature
from opengever.meeting.exceptions import MissingAdHocTemplate
from opengever.meeting.exceptions import MissingMeetingDossierPermissions
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.service import meeting_service
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contentlisting.interfaces import IContentListingObject
from Products.Five.browser import BrowserView
from zExceptions import Forbidden
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
import json


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

    def reopen():
        """Reopen the current agendaitem and make it available for editing
        again.
        """

    def revise():
        """Revise a reopened agenda-item by updating excerpts and prevent
        further editing.
        """

    def edit_document():
        """Checkout and open the document with office connector.
        """

    def generate_excerpt():
        """Create a new excerpt from a agenda item.
        """


class AgendaItemsView(BrowserView):

    implements(IBrowserView, IPublishTraverse)

    def publishTraverse(self, request, name):
        if name in IAgendaItemActions.names():
            return getattr(self, name)

        # we only support exactly one id
        if self.agenda_item_id:
            raise NotFound

        try:
            self.agenda_item_id = int(name)
        except ValueError:
            raise NotFound

        self.agenda_item = meeting_service().fetch_agenda_item(
            self.agenda_item_id)

        if not self.agenda_item:
            raise NotFound

        if self.agenda_item.meeting is not self.meeting:
            # Prevent from cross injections
            raise NotFound

        return self

    def __init__(self, context, request):
        super(AgendaItemsView, self).__init__(context, request)
        self.meeting = self.context.model
        self.agenda_item_id = None
        self.agenda_item = None

    def _serialize_submitted_documents(self, item):
        """Returns a list of html strings (the complete document link).
        """
        if not item.has_proposal:
            return []

        docs = IContentListing(item.proposal.resolve_submitted_documents())
        return [doc.render_link() for doc in docs]

    def _serialize_submitted_excerpt(self, item):
        if not item.has_proposal:
            return None

        excerpt = item.proposal.resolve_submitted_excerpt_document()
        if excerpt:
            return IContentListingObject(excerpt).render_link()

    @require_word_meeting_feature
    def _serialize_excerpts(self, item):
        if not item.has_proposal:
            return []

        submitted_proposal = item.proposal.resolve_submitted_proposal()
        docs = IContentListing(submitted_proposal.get_excerpts())
        return [doc.render_link() for doc in docs]

    @require_word_meeting_feature
    def _get_edit_document_options(self, document, agenda_item, meeting):
        """Return the agenda item options for the template regarding
        editing the document and its lock.
        """
        checkout_manager = getMultiAdapter((document, self.request),
                                           ICheckinCheckoutManager)

        button = {}
        button['visible'] = bool(checkout_manager.check_permission(
            'Modify portal content'))
        button['active'] = button['visible'] and (
            checkout_manager.is_checkout_allowed() or
            checkout_manager.is_checked_out_by_current_user())
        button['url'] = meeting.get_url(
            view='agenda_items/{}/edit_document'.format(
                agenda_item.agenda_item_id))
        return {
            'document_checked_out': bool(
                checkout_manager.get_checked_out_by()),
            'edit_proposal_document_button': button}

    def _get_agenda_items(self):
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
            data['decision_number'] = item.decision_number
            if item.is_decide_possible():
                data['decide_link'] = meeting.get_url(
                    view='agenda_items/{}/decide'.format(item.agenda_item_id))
            if item.is_reopen_possible():
                data['reopen_link'] = meeting.get_url(
                    view='agenda_items/{}/reopen'.format(item.agenda_item_id))
            if item.is_revise_possible():
                data['revise_link'] = meeting.get_url(
                    view='agenda_items/{}/revise'.format(item.agenda_item_id))

            if is_word_meeting_implementation_enabled():
                document = None
                if item.proposal:
                    proposal = item.proposal.submitted_oguid.resolve_object()
                    document = proposal.get_proposal_document()
                elif item.has_document:
                    document = item.resolve_document()

                if document:
                    data['document_link'] = (
                        IContentListingObject(document).render_link())
                    data.update(self._get_edit_document_options(
                        document, item, meeting))

                data['excerpts'] = self._serialize_excerpts(item)
                if self.can_generate_excerpt(item):
                    data['generate_excerpt_link'] = meeting.get_url(
                        view='agenda_items/{}/generate_excerpt'.format(
                            item.agenda_item_id))

            agenda_items.append(data)
        return agenda_items

    def has_documents(self, item):
        if is_word_meeting_implementation_enabled():
            if item.has_document:
                return True

        if not item.has_proposal:
            return False

        return bool(item.proposal.submitted_documents or
                item.proposal.submitted_excerpt_document)

    def list(self):
        """Returns json list of all agendaitems for the current
        context (meeting).
        """

        return JSONResponse(self.request).data(items=self._get_agenda_items()).dump()

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

        title = self.request.get('title')
        if not title:
            return JSONResponse(self.request).error(
                _('agenda_item_update_empty_string',
                  default=u"Agenda Item title must not be empty.")).proceed().dump()

        title = title.decode('utf-8')
        if self.agenda_item.has_proposal:
            if len(title) > ISubmittedProposal['title'].max_length:
                return JSONResponse(self.request).error(
                    _('agenda_item_update_too_long_title',
                      default=u"Agenda Item title is too long.")
                ).proceed().dump()

        self.agenda_item.set_title(title)
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

        self.agenda_item.remove()

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

        error_response = self._checkin_proposal_document_before_deciding()
        if error_response:
            return error_response

        self.agenda_item.decide()

        response = JSONResponse(self.request)
        if self.agenda_item.has_proposal:
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

    def _checkin_proposal_document_before_deciding(self):
        if not is_word_meeting_implementation_enabled():
            # old implementation: there is no proposal document
            return

        if not self.agenda_item.has_proposal:
            # no proposal => no document to checkin
            return

        submitted_proposal = self.agenda_item.proposal.resolve_submitted_proposal()
        document = submitted_proposal.get_proposal_document()
        checkout_manager = getMultiAdapter((document, self.request),
                                           ICheckinCheckoutManager)
        if checkout_manager.get_checked_out_by() is None:
            # document is not checked out
            return

        if not checkout_manager.is_checkin_allowed():
            return JSONResponse(self.request).error(
                _('agenda_item_cannot_decide_document_checked_out',
                  default=u'Cannot decide agenda item: someone else has'
                  u' checked out the document.')).remain().dump()

        checkout_manager.checkin()

    def reopen(self):
        """Reopen the current agendaitem. Set the workflow state to revision
        to indicate that editing is possible again.
        """
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        self.agenda_item.reopen()

        return JSONResponse(self.request).info(
            _(u'agenda_item_reopened',
              default=u'Agenda Item successfully reopened.')).dump()

    def revise(self):
        """Revise the current agendaitem. Set the workflow state to decided
        to indicate that editing is no longer possible.
        """
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        self.agenda_item.revise()

        return JSONResponse(self.request).info(
            _(u'agenda_item_revised',
              default=u'Agenda Item revised successfully.')).dump()

    def edit_document(self):
        """Checkout and open the document with office connector.
        """
        self.check_editable()

        document = self.agenda_item.resolve_document()
        checkout_manager = getMultiAdapter((document, self.request),
                                           ICheckinCheckoutManager)
        response = JSONResponse(self.request)

        if not checkout_manager.is_checked_out_by_current_user() \
           and not checkout_manager.is_checkout_allowed():
            response.remain().error(
                _(u'document_checkout_not_allowed',
                  default=u'You are not allowed to checkout the document.'))
        else:
            url = document.checkout_and_get_office_connector_url()
            response.proceed().data(officeConnectorURL=url)

        return response.dump()

    def schedule_paragraph(self):
        """Schedule the given Paragraph (request parameter `title`) for the current
        meeting.
        """
        self.check_editable()

        title = self.request.get('title')
        if not title:
            return JSONResponse(self.request).error(
                _('empty_paragraph', default=u"Paragraph must not be empty.")).proceed().dump()

        self.meeting.schedule_text(title, is_paragraph=True)
        return JSONResponse(self.request).info(
            _('paragraph_added', default=u"Paragraph successfully added.")
        ).proceed().dump()

    def schedule_text(self):
        """Schedule the given Text (request parameter `title`) for the current
        meeting.
        """
        self.check_editable()
        title = self.request.get('title')
        if not title:
            return JSONResponse(self.request).error(
                    _('empty_proposal', default=u"Proposal must not be empty.")
                ).proceed().dump()

        if is_word_meeting_implementation_enabled():
            try:
                self.meeting.schedule_ad_hoc(title)
            except MissingAdHocTemplate:
                return JSONResponse(self.request).error(
                        _('missing_ad_hoc_template',
                          default=u"No ad-hoc agenda-item template has been "
                                  u"configured.")
                    ).proceed().dump()
            except MissingMeetingDossierPermissions:
                return JSONResponse(self.request).error(
                        _('error_no_permission_to_add_document',
                          default=u'Insufficient privileges to add a'
                                  u' document to the meeting dossier.')
                       ).proceed().dump()

        else:
            self.meeting.schedule_text(title)

        return JSONResponse(self.request).info(
            _('text_added', default=u"Text successfully added.")).proceed().dump()

    def check_editable(self):
        if not self.meeting.is_editable():
            raise Unauthorized("Editing is not allowed")

    def generate_excerpt(self):
        """Generate an excerpt of an agenda item and store it in
        the meeting dossier.
        """
        if not self.context.model.is_editable():
            raise Unauthorized("Editing is not allowed")

        if not self.can_generate_excerpt(self.agenda_item):
            raise Forbidden('Generating excerpt is not allowed in this state.')

        meeting_dossier = self.meeting.get_dossier()
        if not api.user.get_current().checkPermission(
                'opengever.document: Add document', meeting_dossier):
            return (JSONResponse(self.request)
                    .error(_('error_no_permission_to_add_document',
                             default=u'Insufficient privileges to add a'
                             u' document to the meeting dossier.'))
                    .remain()
                    .dump())

        proposal = self.agenda_item.proposal.resolve_submitted_proposal()
        proposal.generate_excerpt(meeting_dossier)
        return (JSONResponse(self.request)
                .info(_('excerpt_generated',
                        default=u'Excerpt was created successfully.'))
                .proceed()
                .dump())

    def can_generate_excerpt(self, agenda_item):
        """Returns True when agenda item and proposal are in a state which
        allows to generate excerpts.
        """
        if not self.context.model.is_editable():
            return False

        return agenda_item.get_state() == agenda_item.STATE_DECIDED
