from five import grok
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from plone.directives.dexterity import DisplayForm
from zope.component import getUtility


class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def get_referenced_documents(self):
        pc = self.context.portal_catalog
        return pc({'portal_type': 'Document', })

    def creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())

