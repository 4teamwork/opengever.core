from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base import advancedjson
from opengever.base.response import IResponseContainer
from opengever.base.security import elevated_privileges
from opengever.base.source import DossierPathSourceBinder
from opengever.base.transport import PrivilegedReceiveObject
from opengever.base.transport import Transporter
from opengever.base.utils import disable_edit_bar
from opengever.document.versioner import Versioner
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.meeting import _
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.activity.activities import ProposalDocumentSubmittedActivity
from opengever.meeting.activity.activities import ProposalDocumentUpdatedActivity
from opengever.meeting.browser.documents.submit import ISubmitAdditionalDocument
from opengever.meeting.exceptions import NoSubmittedDocument
from opengever.meeting.proposalhistory import ProposalResponse
from opengever.tabbedview.utils import get_containing_document_tab_url
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.locking.interfaces import ILockable
from plone.supermodel import model
from Products.Five.browser import BrowserView
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import Unauthorized
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.i18n import translate
from zope.schema import TextLine
import json


class ISubmitAdditionalDocuments(model.Schema):
    """Meeting model schema interface."""

    additionalDocuments = RelationList(
        title=_(u'label_attachments', default=u'Attachments'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                        ['opengever.dossier.behaviors.dossier.IDossierMarker',
                         'opengever.document.document.IDocumentSchema',
                         'opengever.task.task.ITask',
                         'ftw.mail.mail.IMail', ],
                    }),
            ),
        required=True,
        )


class SubmitAdditionalDocuments(AutoExtensibleForm, Form):
    """View for submitting additional documents to an already submitted
    proposal.

    This view is available on proposals to submit multiple documents.

    """
    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX
    label = _(u'label_submit_additional_documents', default=u'Submit Additional Documents')

    schema = ISubmitAdditionalDocuments

    def __call__(self):
        disable_edit_bar()
        return super(SubmitAdditionalDocuments, self).__call__()

    def update(self):
        self._preselect_proposal()
        return super(SubmitAdditionalDocuments, self).update()

    def available(self):
        return is_meeting_feature_enabled() and \
            self.context.is_submit_additional_documents_allowed()

    @buttonAndHandler(_(u'button_submit_attachments',
                        default=u'Submit Attachments'),
                      name='save')
    def submit_documents(self, action):
        data, errors = self.extractData()
        if errors:
            return

        proposal = self.context
        for document in data['additionalDocuments']:
            command = proposal.submit_additional_document(document)
            command.show_message()

        self.request.RESPONSE.redirect(self.nextURL())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()

    def _preselect_proposal(self):
        document_path = self.request.get('document_path')
        if not document_path:
            return

        self.request.set('form.widgets.additionalDocuments', document_path)


class ISubmitDocumentsByPaths(ISubmitAdditionalDocument):

    paths = TextLine(title=u'Selected Items')


class SubmitDocumentsByPaths(AutoExtensibleForm, Form):
    """View for submitting additional documents to an already submitted
    proposal.

    This view is available on proposals to submit multiple documents.

    """

    ignoreContext = True
    schema = ISubmitDocumentsByPaths

    def available(self):
        return is_meeting_feature_enabled()

    @buttonAndHandler(_(u'button_submit_attachments',
                        default=u'Submit Attachments'))
    def submit_documents(self, action):
        data, errors = self.extractData()
        if errors:
            return

        proposal = data['proposal']
        for document in self.get_documents():
            command = proposal.submit_additional_document(document)
            command.show_message()

        self.request.RESPONSE.redirect(self.nextURL())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def updateWidgets(self):
        super(SubmitDocumentsByPaths, self).updateWidgets()
        self.widgets['paths'].mode = HIDDEN_MODE
        self.widgets['paths'].value = ';;'.join(self.get_document_paths())

    def get_documents(self):
        """Return the documents by resolving the submitted paths."""

        docs = []
        portal = api.portal.get()
        for document_path in self.get_document_paths():
            docs.append(
                portal.unrestrictedTraverse(document_path.encode('utf-8')))
        return docs

    def get_document_paths(self):
        """Return document paths from a tabbedview-tab request or from the
        submitted form.

         """
        field_name = self.prefix + self.widgets.prefix + 'paths'
        value = self.request.get(field_name, False)
        if value:
            return value.split(';;')
        return self.request.get('paths', [])

    def nextURL(self):
        return get_containing_document_tab_url(self.context)


class UpdateSubmittedDocumentView(BrowserView):
    """Receives a JSON serialized object and creates or updates an instance
    within its context.

    Returns JSON containing the created object's path and intid.

    """

    def __call__(self):
        if not self.context.is_submitted_document():
            raise NoSubmittedDocument()

        if self.context.is_checked_out():
            raise Unauthorized()

        submitted_proposal = aq_parent(aq_inner(self.context))
        history_data = advancedjson.loads(self.request.get('history_data'))

        with elevated_privileges():
            transporter = Transporter()
            transporter.update(self.context, self.request)

            response = ProposalResponse(
                u'document_updated',
                needs_syncing=False,
                document_title=self.context.title,
                submitted_version=history_data['submitted_version'],
            )
            IResponseContainer(submitted_proposal).add(response)

            ProposalDocumentUpdatedActivity(
                submitted_proposal, self.request,
                self.context.title, history_data['submitted_version']).record()

            portal_path = '/'.join(api.portal.get().getPhysicalPath())
            intids = getUtility(IIntIds)

            comment = translate(
                _(u"Updated with a newer docment version from proposal's "
                  "dossier."), context=self.request)
            Versioner(self.context).create_version(comment)

            data = {
                'path': '/'.join(self.context.getPhysicalPath())[
                    len(portal_path) + 1:],
                'intid': intids.queryId(self.context)
                }

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)


class RecieveSubmittedDocumentView(PrivilegedReceiveObject):
    """Lock submitted documents after recieving them."""

    def receive(self):
        document = super(RecieveSubmittedDocumentView, self).receive()

        history_data = advancedjson.loads(self.request.get('history_data'))
        response = ProposalResponse.deserialize(history_data['response'])
        with elevated_privileges():
            IResponseContainer(self.context).add(response)

        activity = advancedjson.loads(self.request.get('activity'))
        if activity['record_activity']:
            ProposalDocumentSubmittedActivity(
                self.context, self.request, document.title).record()

        ILockable(document).lock(MEETING_SUBMITTED_LOCK)
        return document
