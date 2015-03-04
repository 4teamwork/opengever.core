from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.meeting.browser.proposaltransitions import ProposalTransitionController
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.tabbedview.browser.base import OpengeverTab
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
        return self.context.get_documents()

    def history(self):
        return self.context.load_model().history_records


class ProposalOverview(OverviewBase, DisplayForm, OpengeverTab):
    grok.context(IProposal)
    grok.name('tabbedview_view-overview')
    grok.template('proposaloverview')


class SubmittedProposalOverview(OverviewBase, DisplayForm, OpengeverTab):
    grok.context(ISubmittedProposal)
    grok.name('tabbedview_view-overview')
    grok.template('proposaloverview')
