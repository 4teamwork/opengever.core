from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from functools import wraps
from opengever.base.response import JSONResponse
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.meeting import _
from opengever.meeting.exceptions import CannotExecuteTransition
from opengever.meeting.exceptions import MissingAdHocTemplate
from opengever.meeting.exceptions import MissingMeetingDossierPermissions
from opengever.meeting.exceptions import WrongAgendaItemState
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.sablon import Sablon
from opengever.meeting.service import meeting_service
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.memoize import view
from plone.protect.utils import addTokenToUrl
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
from zExceptions import BadRequest
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView
from ZPublisher.Iterators import filestream_iterator
import json
import os


class IAgendaItemActions(Interface):

    def list():
        """Returns json list of all agendaitems for the current
        context (meeting).
        """

    def edit():
        """Updates the title and description of the current agendaitem,
        with the one given by the request parameters `title` and `description`.
        The view expects that it is called by traversing over the agendaitem:
        `plone/meeting-3/14/edit` for example.
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

    def return_excerpt():
        """Return an excerpt to the proposals dossier.
        """

    def debug_excerpt_docxcompose():
        """Return filled sablon templates agenda item document used to generate
        excerpts as a zipfile. This helps debugging docxcompose.
        """


def return_jsonified_exceptions(func):
    """Decorator for converting common exceptions to JSONResponses.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except (WrongAgendaItemState, CannotExecuteTransition):
            return JSONResponse(getRequest()).error(
                _(u'invalid_agenda_item_state',
                  default=u'The agenda item is in an invalid state for '
                           'this action.'),
                status=403).dump()

        except Forbidden:
            return JSONResponse(getRequest()).error(
                _(u'editing_not_allowed',
                  default=u'Editing is not allowed.'),
                status=403).dump()

        except MissingMeetingDossierPermissions:
            return JSONResponse(getRequest()).error(
                _('error_no_permission_to_add_document',
                  default=u'Insufficient privileges to add a '
                          u'document to the meeting dossier.'),
                status=403).dump()

        except MissingAdHocTemplate:
            return JSONResponse(getRequest()).error(
                _('missing_ad_hoc_template',
                  default=u"No ad-hoc agenda-item template has been "
                          u"configured."),
                status=501).dump()

    return wrapper


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
        return [doc.render_link() for doc in sorted(docs, key=lambda doc: doc.title_or_id().lower())]

    def _serialize_submitted_excerpt(self, item):
        if not item.has_proposal:
            return None

        excerpt = item.proposal.resolve_submitted_excerpt_document()
        if excerpt:
            return IContentListingObject(excerpt).render_link()

    def _serialize_excerpts(self, meeting, item):
        excerpt_data = []

        docs = IContentListing(item.get_excerpt_documents(unrestricted=True))
        source_dossier_excerpt = item.get_source_dossier_excerpt()
        meeting_dossier = self.meeting.get_dossier()

        for doc in docs:
            data = {'link': doc.render_link()}
            if not source_dossier_excerpt and item.has_proposal:
                if self.meeting.is_editable():
                    data['return_link'] = meeting.get_url(
                        view='agenda_items/{}/return_excerpt?document={}'.format(
                            item.agenda_item_id, doc.uuid()))

            elif source_dossier_excerpt and doc == source_dossier_excerpt:
                data['is_excerpt_in_source_dossier'] = True

            if self._can_add_task_to_meeting_dossier():
                data['create_task_url'] = addTokenToUrl(
                    '{}/++add++opengever.task.task?paths:list={}'.format(
                        meeting_dossier.absolute_url(),
                        doc.getPath()))

            excerpt_data.append(data)

        return excerpt_data

    @view.memoize
    def _can_add_task_to_meeting_dossier(self):
        return self.meeting.get_dossier().is_addable('opengever.task.task')

    def _get_edit_document_options(self, document, agenda_item, meeting):
        """Return the agenda item options for the template regarding
        editing the document and its lock.
        """
        checkout_manager = getMultiAdapter((document, self.request),
                                           ICheckinCheckoutManager)

        button = {}
        button['visible'] = bool(
            checkout_manager.check_permission('Modify portal content')
            and not agenda_item.is_decided())
        button['active'] = button['visible'] and (
            checkout_manager.is_checkout_allowed()
            or checkout_manager.is_checked_out_by_current_user())
        button['url'] = meeting.get_url(
            view='agenda_items/{}/edit_document'.format(
                agenda_item.agenda_item_id))
        return {
            'document_checked_out': bool(
                checkout_manager.get_checked_out_by()),
            'edit_document_button': button}

    def _get_agenda_items(self):
        meeting = self.meeting
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
            data['decision_number'] = item.get_decision_number()
            data['is_decided'] = item.is_decided()
            if item.is_decide_possible():
                data['decide_link'] = meeting.get_url(
                    view='agenda_items/{}/decide'.format(item.agenda_item_id))
            if item.is_reopen_possible():
                data['reopen_link'] = meeting.get_url(
                    view='agenda_items/{}/reopen'.format(item.agenda_item_id))
            if item.is_revise_possible():
                data['revise_link'] = meeting.get_url(
                    view='agenda_items/{}/revise'.format(item.agenda_item_id))
            if item.is_paragraph:
                data['paragraph'] = True

            document = item.resolve_document()
            if document:
                data['document_link'] = (
                    IContentListingObject(document).render_link())
                data.update(self._get_edit_document_options(
                    document, item, meeting))

            data['excerpts'] = self._serialize_excerpts(meeting, item)
            if item.can_generate_excerpt():
                data['generate_excerpt_default_title'] = translate(
                    _(u'excerpt_document_default_title',
                      default=u'Excerpt ${title}',
                      mapping={'title': safe_unicode(item.get_title())}),
                    context=self.request,
                ).strip()
                data['generate_excerpt_link'] = meeting.get_url(
                    view='agenda_items/{}/generate_excerpt'.format(
                        item.agenda_item_id))

            if item.is_decided():
                data['css_class'] += ' decided'

            agenda_items.append(data)
        return agenda_items

    def has_documents(self, item):
        return item.has_submitted_documents()

    def list(self):
        """Returns json list of all agendaitems for the current
        context (meeting).
        """
        return JSONResponse(self.request).data(items=self._get_agenda_items()).dump()

    @return_jsonified_exceptions
    def update_order(self):
        """Updates the order of the agendaitems. The new sortOrder is expected
        in the request parameter `sortOrder`.
        """
        self.require_agendalist_editable()

        self.meeting.reorder_agenda_items(
            json.loads(self.request.get('sortOrder')))

        return JSONResponse(self.request).info(
            _('agenda_item_order_updated',
              default=u"Agenda Item order updated.")).dump()

    @return_jsonified_exceptions
    def edit(self):
        """Updates the title of the agendaitem, with the one given by the
        request parameter `title`.
        """
        self.require_agendalist_editable()

        title = safe_unicode(self.request.get('title'))
        description = safe_unicode(self.request.get('description'))

        if not title:
            return JSONResponse(self.request).error(
                _('agenda_item_update_empty_string',
                  default=u"Agenda Item title must not be empty.")).proceed().dump()

        if self.agenda_item.has_proposal:
            if len(title) > ISubmittedProposal['title'].max_length:
                return JSONResponse(self.request).error(
                    _('agenda_item_update_too_long_title',
                      default=u"Agenda Item title is too long.")
                ).proceed().dump()

        self.agenda_item.set_title(title)
        self.agenda_item.set_description(description)
        return JSONResponse(self.request).info(
            _('agenda_item_updated',
              default=u"Agenda Item updated.")).proceed().dump()

    @return_jsonified_exceptions
    def delete(self):
        """Unschedule the current agenda_item. If the agenda_item has no
        proposal, the agenda_item gets deleted. If there is a proposal related,
        the proposal is unscheduled.
        """
        self.require_agendalist_editable()

        self.agenda_item.remove()

        return JSONResponse(self.request).info(
            _(u'agenda_item_deleted',
              default=u'Agenda Item Successfully deleted')).dump()

    @return_jsonified_exceptions
    def decide(self):
        """Decide the current agendaitem and move the meeting in the
        held state.
        """
        self.require_editable()

        meeting_state = self.meeting.get_state()
        error_response = self._checkin_proposal_document_before_deciding()
        if error_response:
            return error_response

        self.agenda_item.decide()

        response = JSONResponse(self.request)
        response.info(_(u'agenda_item_decided',
                        default=u'Agenda Item decided.'))

        if meeting_state != self.meeting.get_state():
            response.redirect(self.context.absolute_url())
            msg = _(u'agenda_item_meeting_held',
                default=u"Agendaitem has been decided and the meeting has been held.")
            api.portal.show_message(message=msg, request=self.request, type='info')

        return response.dump()

    def _checkin_proposal_document_before_deciding(self):
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

    @return_jsonified_exceptions
    def reopen(self):
        """Reopen the current agendaitem. Set the workflow state to revision
        to indicate that editing is possible again.
        """
        self.require_editable()

        self.agenda_item.reopen()

        return JSONResponse(self.request).info(
            _(u'agenda_item_reopened',
              default=u'Agenda Item successfully reopened.')).dump()

    @return_jsonified_exceptions
    def revise(self):
        """Revise the current agendaitem. Set the workflow state to decided
        to indicate that editing is no longer possible.
        """
        self.require_editable()

        self.agenda_item.revise()
        return JSONResponse(self.request).info(
            _(u'agenda_item_revised',
              default=u'Agenda Item revised successfully.')).dump()

    @return_jsonified_exceptions
    def edit_document(self):
        """Checkout and open the document with office connector.
        """
        self.require_editable()

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

    @return_jsonified_exceptions
    def schedule_paragraph(self):
        """Schedule the given Paragraph (request parameter `title`) for the current
        meeting.
        """
        self.require_agendalist_editable()

        title = self.request.get('title')
        if not title:
            return JSONResponse(self.request).error(
                _('empty_paragraph', default=u"Paragraph must not be empty.")).proceed().dump()

        self.meeting.schedule_text(title, is_paragraph=True)
        return JSONResponse(self.request).info(
            _('paragraph_added', default=u"Paragraph successfully added.")
        ).proceed().dump()

    @return_jsonified_exceptions
    def schedule_text(self):
        """Schedule the given Text (request parameterd `title` and description) for the current
        meeting.
        """
        self.require_agendalist_editable()

        title = safe_unicode(self.request.get('title'))
        description = safe_unicode(self.request.get('description'))
        if not title:
            return JSONResponse(self.request).error(
                    _('empty_proposal', default=u"Proposal must not be empty.")
                ).proceed().dump()

        template = safe_unicode(self.request.get('template_id'))
        self.meeting.schedule_ad_hoc(title, template_id=template,
                                     description=description)

        return JSONResponse(self.request).info(
            _('text_added', default=u"Text successfully added.")).proceed().dump()

    def require_editable(self):
        if not self.meeting.is_editable():
            raise Forbidden("Editing is not allowed")

    def require_agendalist_editable(self):
        if not self.meeting.is_agendalist_editable():
            raise Forbidden("Editing is not allowed")

    @return_jsonified_exceptions
    def generate_excerpt(self):
        """Generate an excerpt of an agenda item and store it in
        the meeting dossier.
        """
        self.require_editable()

        title = safe_unicode(self.request.form['excerpt_title'])
        self.agenda_item.generate_excerpt(title=title)

        return (JSONResponse(self.request)
                .info(_('excerpt_generated',
                        default=u'Excerpt was created successfully.'))
                .proceed()
                .dump())

    @return_jsonified_exceptions
    def return_excerpt(self):
        """Return an excerpt for a proposal to the dossier the proposal
        originated from.
        """
        doc_uuid = self.request.get('document')
        if not doc_uuid:
            raise BadRequest("No excerpt document provided.")

        document = self._get_excerpt_doc_by_uuid(doc_uuid)
        if not document:
            raise NotFound(
                "Could not find excerpt document {}".format(doc_uuid))

        self.agenda_item.return_excerpt(document)
        return (JSONResponse(self.request)
                .info(_('excerpt_returned',
                        default=u'Excerpt was returned to proposer.'))
                .proceed()
                .dump())

    def _get_excerpt_doc_by_uuid(self, doc_uuid):
        excerpts = self.agenda_item.proposal.resolve_submitted_proposal().get_excerpts()

        for doc in excerpts:
            if IUUID(doc) == doc_uuid:
                return doc
        return None

    def debug_excerpt_docxcompose(self):
        if not api.user.has_permission('cmf.ManagePortal'):
            raise Forbidden

        if self.agenda_item.is_paragraph:
            raise NotFound

        excerpt_protocol_data = ExcerptProtocolData(
            self.meeting, [self.agenda_item])

        header_template = self.agenda_item.get_excerpt_header_template()
        suffix_template = self.agenda_item.get_excerpt_suffix_template()

        with ZipGenerator() as generator:
            if header_template:
                sablon = Sablon(header_template).process(
                    excerpt_protocol_data.as_json())
                generator.add_file(
                    u'000_excerpt_header_template.docx',
                    StringIO(sablon.file_data))

            document = self.agenda_item.resolve_document()
            filename = u'001_agenda_item_{}.docx'.format(
                safe_unicode(document.Title()))
            generator.add_file(filename, document.file.open())

            if suffix_template:
                sablon = Sablon(suffix_template).process(
                    excerpt_protocol_data.as_json())
                generator.add_file(
                    u'002_excerpt_suffix_template.docx',
                    StringIO(sablon.file_data))

            # Return zip
            response = self.request.response
            zip_file = generator.generate()
            filename = '{}.zip'.format(normalize_path(self.meeting.title))
            response.setHeader(
                "Content-Disposition",
                'inline; filename="{0}"'.format(
                    safe_unicode(filename).encode('utf-8')))
            response.setHeader("Content-type", "application/zip")
            response.setHeader(
                "Content-Length",
                os.stat(zip_file.name).st_size)

            return filestream_iterator(zip_file.name, 'rb')
