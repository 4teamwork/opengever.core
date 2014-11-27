from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.meeting.proposal import IProposal
from opengever.tabbedview.browser.base import OpengeverTab
from plone.directives.dexterity import DisplayForm


class ProposalOverview(DisplayForm, OpengeverTab):
    grok.context(IProposal)
    grok.name('tabbedview_view-overview')
    grok.template('proposaloverview')

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
