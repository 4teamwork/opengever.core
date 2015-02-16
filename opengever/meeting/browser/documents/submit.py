from opengever.base.source import DossierPathSourceBinder
from opengever.document import _
from opengever.meeting.proposal import IProposal
from plone import api
from plone.autoform.form import AutoExtensibleForm
from plone.directives import form
from plone.formwidget.contenttree.source import CustomFilter
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from z3c.relationfield.schema import RelationChoice


class SubmittableProposalFilter(CustomFilter):
    """Custom selectable filter to only allow selection of proposals which
    allow submission of additional documents.

    """
    def __call__(self, brain, index_data):
        obj = brain.getObject()
        if IProposal.providedBy(obj):
            return IProposal(obj).is_submit_additional_documents_allowed()
        return super(SubmittableProposalFilter, self).__call__(
            brain, index_data)


class ISubmitAdditionalDocument(form.Schema):

    proposal = RelationChoice(
        title=_(u'Proposal', default=u'Proposal'),
        source=DossierPathSourceBinder(
            filter_class=SubmittableProposalFilter,
            portal_type=("opengever.meeting.proposal"),
            navigation_tree_query={
                'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.meeting.proposal.IProposal'],
                }),
        )


class SubmitAdditionalDocument(AutoExtensibleForm, Form):
    """View for submitting an additional document to an already made proposal.

    """
    ignoreContext = True

    schema = ISubmitAdditionalDocument

    @buttonAndHandler(_(u'button_submit_document', default=u'Submit Document'))
    def submit_documents(self, action):
        data, errors = self.extractData()
        if errors:
            return

        proposal = data['proposal']
        document = self.context
        if proposal.submit_additional_document(document):
            api.portal.show_message(
                _(u'This document was already submitted in that version.'),
                self.request,
                type='warn')

        api.portal.show_message(
            _(u'Additional document has been submitted successfully'),
            self.request)
        self.request.RESPONSE.redirect(self.nextURL())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()
