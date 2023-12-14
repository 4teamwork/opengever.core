from ftw.bumblebee.interfaces import IBumblebeeDocument
from plone import api
from plone.rest import Service
from plone.restapi.services.locking.locking import lock_info
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import json


class DocumentStatus(Service):
    """Provide information on the current status of a document."""

    def render(self):
        payload = {}
        payload['int_id'] = getUtility(IIntIds).getId(self.context)
        payload['title'] = self.context.title_or_id()
        payload['checkout_collaborators'] = list(self.context.get_collaborators())
        payload['checked_out'] = self.context.is_checked_out()
        payload['checked_out_collaboratively'] = self.context.is_collaborative_checkout()
        payload['checked_out_by'] = self.context.checked_out_by()
        payload['bumblebee_checksum'] = IBumblebeeDocument(self.context).get_checksum()

        info = lock_info(self.context)
        payload['locked'] = info['locked']
        payload['locked_by'] = info.get('creator')
        payload['lock_time'] = info.get('time')
        payload['lock_timeout'] = info.get('timeout')

        payload['file_mtime'] = self.context.get_file_mtime()

        payload['review_state'] = api.content.get_state(self.context)

        return json.dumps(payload)


class DefaultEmailAttributes(Service):
    """Prevent action send as attachment to fail."""

    def render(self):
        return json.dumps({})
