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
        if self.is_meeting_lock():
            return self.meeting_lock_template()

        return super(GeverLockInfoViewlet, self).render()

    def is_meeting_lock(self):
        lock_info = self.lock_info()
        if not lock_info:
            return False

        lock_type = lock_info.get('type')
        if not lock_type:
            return False

        return lock_type.__name__ == LOCK_TYPE_SYS_LOCK

    def get_related_meeting_from_protocol(self):
        oguid = Oguid.for_object(self.context)
        protocol = GeneratedProtocol.get_one(oguid=oguid)
        return protocol.meeting
