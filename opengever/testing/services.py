from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.services import Service
from zope.interface import alsoProvides


class WriteOnRead(Service):
    """API Endpoint that simulates a write-on-read in tests.

    (In the context of ReadOnlyErrors - not CSRF protection).
    """

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.context.some_attribute = 'foo'

    def check_permission(self):
        return
