from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.document import _ as document_mf
from opengever.meeting.browser.proposaltransitions import ProposalTransitionController
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.tabbedview import GeverTabMixin
from plone.app.contentlisting.interfaces import IContentListing
from plone.directives.dexterity import DisplayForm


class OverviewBase(object):

    def transitions(self):
        return self.context.get_transitions()

    def transition_url(self, transition):
        return ProposalTransitionController.url_for(self.context, transition.name)

    def get_main_attributes(self):
        """ return a list of widgets,
        which should be displayed in the attributes box
        """

        return self.context.get_overview_attributes()

    def get_css_class(self, item):
        """Return the sprite-css-class for the given object.
        """
        css = get_css_class(item)
        return '{} {}'.format("rollover-breadcrumb", css)

    def documents(self):
        return IContentListing(self.context.get_documents())

    def excerpt(self):
        return self.context.get_excerpt()

    def history(self):
        return self.context.load_model().history_records

    def is_update_outdated_endabled(self):
        """We don't want to display the link to update outdated
        document-versions for submitted proposals.
        It's possible that the original document is not available
        from the submitted proposal because it is located on a different
        plone site.
        """
        return not ISubmittedProposal.providedBy(self.context)


class ProposalOverview(OverviewBase, DisplayForm, GeverTabMixin):
    grok.context(IProposal)
    grok.name('tabbedview_view-overview')
    grok.template('proposaloverview')
    grok.require('zope2.View')

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
            mapping={'version': document.getObject().get_current_version()})


class SubmittedProposalOverview(OverviewBase, DisplayForm, GeverTabMixin):
    grok.context(ISubmittedProposal)
    grok.name('tabbedview_view-overview')
    grok.template('proposaloverview')
    grok.require('zope2.View')
