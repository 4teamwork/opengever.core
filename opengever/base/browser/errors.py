from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import Interface


class ErrorHandlingView(BrowserView):
    adapts(Exception, Interface)
    template = ViewPageTemplateFile('templates/error.pt')

    def __call__(self):
        self.plone = getSite()

        if self.plone:
            self.portal_state = self.plone.unrestrictedTraverse(
                '@@plone_portal_state')
            self.portal_url = self.portal_state.portal_url()
            self.language = self.portal_state.language()
        else:
            self.portal_state = None
            self.portal_url = ''
            self.language = 'de'

        exception = self.context
        self.error_type = type(exception).__name__

        return self.template()

    def is_manager(self):
        if self.plone:
            return api.user.has_permission('cmf.ManagePortal')
