from five import grok
from opengever.base.source import DossierPathSourceBinder
from opengever.base.transport import Transporter
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.meeting import is_meeting_feature_enabled
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import json


class ISubmitAdditionalDocuments(form.Schema):
    """Meeting model schema interface."""

    additionalDocuments = RelationList(
        title=_(u'label_documents', default=u'Documents'),
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

    schema = ISubmitAdditionalDocuments

    def available(self):
        return is_meeting_feature_enabled() and \
            self.context.is_submit_additional_documents_allowed()

    @buttonAndHandler(_(u'button_submit_documents', default=u'Submit Documents'))
    def submit_documents(self, action):
        data, errors = self.extractData()
        if errors:
            return

        proposal = self.context
        for document in data['additionalDocuments']:
            proposal.submit_additional_document(document)

        api.portal.show_message(
            _(u'Additional documents have been submitted successfully'),
            self.request)
        self.request.RESPONSE.redirect(self.nextURL())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()


class ReceiveObject(grok.View):
    """Receives a JSON serialized object and creates or updates an instance
    within its context.

    Returns JSON containing the created object's path and intid.

    """
    grok.name('update-submitted-document')
    grok.require('cmf.AddPortalContent')
    grok.context(IDocumentSchema)

    # XXX only allow if document is in a submitted proposal
    # XXX only allow if document is not checked out
    def render(self):
        transporter = Transporter()
        transporter.update(self.context, self.request)

        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        intids = getUtility(IIntIds)
        repository = api.portal.get_tool('portal_repository')
        comment = _(u"Updated with a newer docment version from proposal's "
                    "dossier.")
        repository.save(obj=self.context, comment=comment)

        data = {
            'path': '/'.join(self.context.getPhysicalPath())[
                len(portal_path) + 1:],
            'intid': intids.queryId(self.context)
            }

        # Set correct content type for JSON response
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(data)
