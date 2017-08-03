from ftw.mail.interfaces import IEmailAddress
from plone.rest import Service

import json


class DossierAttributes(Service):
    """Provide get accessors to dossier attributes."""

    def render(self):
        payload = {}
        payload['email'] = IEmailAddress(
            self.request).get_email_for_object(self.context)
        return json.dumps(payload)
