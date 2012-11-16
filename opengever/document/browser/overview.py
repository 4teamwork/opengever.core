from five import grok
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from plone.directives.dexterity import DisplayForm
from zope.component import getUtility
from opengever.base.browser.helper import get_css_class



class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())

    def get_css_class(self):
        return get_css_class(self.context)

