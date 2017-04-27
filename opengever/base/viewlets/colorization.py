from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import os


COLORS = {
    'red': '#C3375A',
    'yellow': '#EBD21E',
    'green': '#37C35A'}

ENVIRONMENT_KEY = 'GEVER_COLORIZATION'


class ColorizationViewlet(ViewletBase):

    index = ViewPageTemplateFile('colorization.pt')

    def css(self):
        colorname = os.environ.get(ENVIRONMENT_KEY, None)
        if colorname is not None:
            return "div.contentWrapper {border: 5px solid %s;}" % COLORS.get(
                colorname, colorname)
        return None
