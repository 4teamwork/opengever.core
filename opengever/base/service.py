from plone.rest import Service
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
import json


class DocumentStatus(Service):
    """Provide information on the current status of a document."""

    def render(self):
        lock_manager = getMultiAdapter(
            (self.context, self.request), name='plone_lock_info')

        payload = {}
        payload['int_id'] = getUtility(IIntIds).getId(self.context)
        payload['title'] = self.context.title_or_id()
        payload['checked_out'] = self.context.is_checked_out()
        payload['checked_out_collaboratively'] = self.context.is_collaborative_checkout()
        payload['checked_out_by'] = self.context.checked_out_by()
        payload['locked'] = lock_manager.is_locked()
        if lock_manager.lock_info():
            payload['locked_by'] = lock_manager.lock_info()['creator']
        else:
            payload['locked_by'] = None

        return json.dumps(payload)


class DefaultEmailAttributes(Service):
    """Prevent action send as attachment to fail."""

    def render(self):
        return json.dumps({})
