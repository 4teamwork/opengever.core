from ftw.mail.interfaces import IEmailAddress
from plone import api
from plone.rest import Service
import json


class DossierAttributes(Service):
    """Provide get accessors to dossier attributes."""

    def render(self):
        payload = {}
        if api.user.has_permission('Modify portal content', obj=self.context):
            payload['email'] = IEmailAddress(
                self.request).get_email_for_object(self.context)
        return json.dumps(payload)
