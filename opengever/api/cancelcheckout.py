from opengever.api import _
from opengever.document.interfaces import ICheckinCheckoutManager
from plone.restapi.services import Service
from zExceptions import Forbidden
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
import plone.protect.interfaces


class CancelCheckout(Service):
    """Cancel an existing checkout of a document"""

    def reply(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)

        if not manager.is_cancel_allowed():
            raise Forbidden(_('msg_cancel_checkout_disallowed',
                              default=u'Cancel checkout is not allowed.'))

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        manager.cancel()
        self.request.response.setStatus(204)
        return super(CancelCheckout, self).reply()
