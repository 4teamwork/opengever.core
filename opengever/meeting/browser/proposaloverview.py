from ftw import bumblebee
from opengever.base.browser.helper import get_css_class
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document import _ as document_mf
from opengever.document.widgets.document_link import DocumentLinkWidget
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.proposal import ISubmittedProposal
from opengever.meeting.proposal_transition_comment import ProposalTransitionCommentAddForm
from opengever.tabbedview import GeverTabMixin
from plone.app.contentlisting.interfaces import IContentListing
from plone.dexterity.browser import view


class OverviewBase(object):

    def transitions(self):
        return self.context.get_transitions()

    def transition_url(self, transition):
        return ProposalTransitionCommentAddForm.url_for(self.context, transition.name)

    def is_comment_allowed(self):
        return self.context.can_comment()

    def comment_url(self):
        return '%s/addcomment' % self.context.absolute_url()

    def get_main_attributes(self):
        """ return a list of widgets,
        which should be displayed in the attributes box
        """

        return self.context.get_overview_attributes()

    def get_css_class(self, item):
        """Return the sprite-css-class for the given object.
        """
        return ' '.join(['rollover-breadcrumb', get_css_class(item)])

    def documents(self):
        return IContentListing(self.context.get_documents())

    def excerpt(self):
        return self.context.get_excerpt()

    def history(self):
        return IHistory(self.context)

    def is_update_outdated_endabled(self):
        """We don't want to display the link to update outdated
        document-versions for submitted proposals.
        It's possible that the original document is not available
        from the submitted proposal because it is located on a different
        plone site.
        """
        return not ISubmittedProposal.providedBy(self.context)

    def show_preview(self):
        return (
            is_bumblebee_feature_enabled()
            and self.context.get_proposal_document() is not None
        )

    def get_preview_image_url(self):
        return bumblebee.get_service_v3().get_representation_url(
            self.context.get_proposal_document(), 'image')

    def get_overlay_url(self):
        return '{}/@@bumblebee-overlay-document'.format(
            self.context.get_proposal_document().absolute_url())

    def is_create_successor_proposal_button_visible(self):
        """Returns True when the "Create successor proposal" should be
        displayed.
        """
        if ISubmittedProposal.providedBy(self.context):
            return False

        model = self.context.load_model()
        return model.get_state() == model.STATE_DECIDED

    def render_protocol_excerpt_document_link(self):
        excerpt = self.context.get_excerpt()
        if excerpt:
            return DocumentLinkWidget(excerpt).render()
        return u''


class ProposalOverview(OverviewBase, view.DefaultView, GeverTabMixin):

    def get_submitted_document(self, document):
        return SubmittedDocument.query.get_by_source(
            self.context, document.getObject())

    def get_update_document_url(self, document):
        return '{}/@@submit_additional_documents?document_path={}'.format(
            self.context.absolute_url(),
            '/'.join(document.getObject().getPhysicalPath())

        )

    def is_outdated(self, document, submitted_document):
        return not submitted_document.is_up_to_date(document.getObject())

    def render_submitted_version(self, submitted_document):
        return document_mf(
            u"Submitted version: ${version}",
            mapping={'version': submitted_document.submitted_version})

    def render_current_document_version(self, document):
        return document_mf(
            u"Current version: ${version}",
            mapping={'version': document.getObject().get_current_version_id(
                missing_as_zero=True)})


class SubmittedProposalOverview(OverviewBase, view.DefaultView, GeverTabMixin):
    """
    """
