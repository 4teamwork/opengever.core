from Products.Five.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile


class View(BrowserView):

    template = ViewPageTemplateFile('templates/macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]
