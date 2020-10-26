from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from zope.interface import alsoProvides


class WriteOnRead(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.context.some_attribute = 'foo'
