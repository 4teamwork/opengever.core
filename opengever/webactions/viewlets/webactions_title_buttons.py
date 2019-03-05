from opengever.webactions.interfaces import IWebActionsRenderer
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class WebactionsTitleButtons(common.ViewletBase):

    index = ViewPageTemplateFile('webactions_title_buttons.pt')

    def get_webactions(self):
        renderer = getMultiAdapter((self.context, self.request),
                                   IWebActionsRenderer, name='title-buttons')
        return renderer()
