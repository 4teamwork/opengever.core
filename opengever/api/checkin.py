from opengever.document.interfaces import ICheckinCheckoutManager
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import plone.protect.interfaces


class Checkin(Service):
    """Check-in a document"""

    def reply(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)

        if not manager.is_checkin_allowed():
            self.request.response.setStatus(403)
            return {'error': {
                'type': 'Forbidden',
                'message': 'Checkin is not allowed.',
            }}

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        comment = data.get('comment', '')

        manager.checkin(comment=comment)
        self.request.response.setStatus(204)
        return super(Checkin, self).reply()
