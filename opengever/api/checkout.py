from opengever.document.interfaces import ICheckinCheckoutManager
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import plone.protect.interfaces


class Checkout(Service):
    """Check-out a document"""

    def reply(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)

        if not manager.is_checkout_allowed():
            self.request.response.setStatus(403)
            return {'error': {
                'type': 'Forbidden',
                'message': 'Checkout is not allowed.',
            }}

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        manager.checkout()
        self.request.response.setStatus(204)
        return super(Checkout, self).reply()
