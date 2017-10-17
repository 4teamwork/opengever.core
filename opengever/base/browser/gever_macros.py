from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class View(BrowserView):

    template = ViewPageTemplateFile('templates/gever-macros.pt')

    def __getitem__(self, key):
        return self.template.macros[key]
