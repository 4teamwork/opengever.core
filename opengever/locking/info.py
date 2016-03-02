from opengever.base.oguid import Oguid
from opengever.locking.lock import LOCK_TYPE_SYS_LOCK
from opengever.meeting.model import GeneratedProtocol
from plone.locking.browser.info import LockInfoViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GeverLockInfoViewlet(LockInfoViewlet):
    """Locking Info Viewlet which renders different templates
    for different locking types.
    """
    meeting_lock_template = ViewPageTemplateFile('templates/meeting_lock.pt')

    def render(self):
        lock_info = self.info.lock_info()
        if lock_info and lock_info.get('type').__name__ == LOCK_TYPE_SYS_LOCK:
            return self.meeting_lock_template()

        return super(GeverLockInfoViewlet, self).render()

    def get_related_meeting_from_protocol(self):
        oguid = Oguid.for_object(self.context)
        protocol = GeneratedProtocol.get_one(oguid=oguid)
        return protocol.meeting
