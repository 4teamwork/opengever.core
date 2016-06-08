from opengever.base.oguid import Oguid
from opengever.locking.lock import LOCK_TYPE_MEETING_SUBMITTED_LOCK
from opengever.locking.lock import LOCK_TYPE_SYS_LOCK
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import SubmittedDocument
from plone.locking.browser.info import LockInfoViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GeverLockInfoViewlet(LockInfoViewlet):
    """Locking Info Viewlet which renders different templates
    for different locking types.
    """
    meeting_lock_template = ViewPageTemplateFile(
        'templates/meeting_lock.pt')
    submitted_document_lock_template = ViewPageTemplateFile(
        'templates/submitted_document_lock_template.pt')

    # templates seem to be converted to BoundPageTemplate with acquisition
    # magic, thus we cannot put the ViewPageTemplateFile instances directly
    # into the mapping
    custom_templates = {
        LOCK_TYPE_SYS_LOCK: 'meeting_lock_template',
        LOCK_TYPE_MEETING_SUBMITTED_LOCK: 'submitted_document_lock_template',
    }

    def render(self):
        custom_template_name = self.custom_templates.get(
            self.get_lock_type_name())
        if custom_template_name:
            return getattr(self, custom_template_name)()

        return super(GeverLockInfoViewlet, self).render()

    def get_lock_type_name(self):
        lock_info = self.lock_info()
        if not lock_info:
            return None

        lock_type = lock_info.get('type')
        if not lock_type:
            return None

        return lock_type.__name__

    def get_related_meeting_from_protocol(self):
        oguid = Oguid.for_object(self.context)
        protocol = GeneratedProtocol.get_one(oguid=oguid)
        return protocol.meeting

    def get_source_document_from_submitted_document(self):
        document = SubmittedDocument.query.get_by_target(self.context)
        return document.resolve_source()if document else None
