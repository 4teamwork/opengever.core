from opengever.base.source import DossierPathSourceBinder
from opengever.base.utils import disable_edit_bar
from opengever.meeting import _
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.proposal import IProposal
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
        required=True
        )


class SubmitAdditionalDocument(AutoExtensibleForm, Form):
    """View for submitting an additional document to an already made proposal.

    """
    ignoreContext = True

    schema = ISubmitAdditionalDocument

    def available(self):
        return is_meeting_feature_enabled() and \
            self.context.can_be_submitted_as_additional_document()

    def __call__(self):
        disable_edit_bar()
        return super(SubmitAdditionalDocument, self).__call__()

    @buttonAndHandler(_(u'button_submit_document', default=u'Submit Document'))
    def submit_documents(self, action):
        data, errors = self.extractData()
        if errors:
            return

        proposal = data['proposal']
        document = self.context
        command = proposal.submit_additional_document(document)
        command.show_message()

        self.request.RESPONSE.redirect(self.nextURL())

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.nextURL())

    def nextURL(self):
        return self.context.absolute_url()
