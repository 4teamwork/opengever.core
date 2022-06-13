from opengever.base.colorization import get_color
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ColorizationViewlet(ViewletBase):

    index = ViewPageTemplateFile('colorization.pt')

    def css(self):
        colorname = get_color()
        if colorname is not None:
            return "div.contentWrapper {border: 5px solid %s;}" % colorname
        return None
