from opengever.base.oguid import Oguid
from opengever.locking.lock import LOCK_TYPE_MEETING_EXCERPT_LOCK
from opengever.locking.lock import LOCK_TYPE_MEETING_SUBMITTED_LOCK
from opengever.meeting.model import GeneratedExcerpt
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import SubmittedDocument
from plone import api
from plone.locking.browser.info import LockInfoViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.interfaces import IEditForm


class GeverLockInfoViewlet(LockInfoViewlet):
    """Locking Info Viewlet which renders different templates
    for different locking types.
    """
    submitted_document_lock_template = ViewPageTemplateFile(
        'templates/submitted_document_lock_template.pt')
    excerpt_document_lock_template = ViewPageTemplateFile(
        'templates/excerpt_document_lock_template.pt')
    oc_document_lock_template = ViewPageTemplateFile(
        'templates/oc_document_lock_template.pt')
    default_template = ViewPageTemplateFile('templates/info.pt')

    # templates seem to be converted to BoundPageTemplate with acquisition
    # magic, thus we cannot put the ViewPageTemplateFile instances directly
    # into the mapping
    custom_templates = {
        LOCK_TYPE_MEETING_SUBMITTED_LOCK: 'submitted_document_lock_template',
        LOCK_TYPE_MEETING_EXCERPT_LOCK: 'excerpt_document_lock_template',
        "office_connector_lock": 'oc_document_lock_template',
        'default': 'default_template'
    }

    def render(self):
        custom_template_name = self.get_template_name()
        return getattr(self, custom_template_name)()

    def get_template_name(self):
        custom_template_name = self.custom_templates.get(
            self.get_lock_type_name(), self.custom_templates.get('default'))
        return custom_template_name

    def get_lock_type_name(self):
        lock_info = self.lock_info()
        if not lock_info:
            return None
        lock_type = lock_info.get('type')
        owner = lock_info.get('owner')
        if not lock_type and owner == '<D:href>Office Connector</D:href>':
            return "office_connector_lock"
        return getattr(lock_type, "__name__", None)

    def current_user_can_unlock_document(self):
        return "Manager" in api.user.get_roles()

    def is_edit_form(self):
        return (IEditForm.providedBy(self.view)
                or IEditForm.providedBy(getattr(self.view, "form_instance", None)))

    def get_related_meeting_from_protocol(self):
        oguid = Oguid.for_object(self.context)
        protocol = GeneratedProtocol.get_one(oguid=oguid)
        return protocol.meeting

    def get_source_document_from_submitted_document(self):
        document = SubmittedDocument.query.get_by_target(self.context)
        return document.resolve_source()if document else None

    def _get_proposal_from_dossier_excerpt(self):
        if not hasattr(self, '_proposal_from_dossier_excerpt'):
            self._proposal_from_dossier_excerpt = None
            excerpt_in_dossier = GeneratedExcerpt.query.by_document(self.context).first()
            if excerpt_in_dossier:
                self._proposal_from_dossier_excerpt = excerpt_in_dossier.proposal

        return self._proposal_from_dossier_excerpt

    def get_meeting_excerpt_from_dossier_excerpt(self):
        proposal = self._get_proposal_from_dossier_excerpt()
        if not proposal:
            return None

        excerpt_in_meeting = proposal.submitted_excerpt_document.resolve_document()
        return excerpt_in_meeting

    def get_meeting_from_dossier_excerpt(self):
        proposal = self._get_proposal_from_dossier_excerpt()
        if not proposal:
            return None

        agenda_item = proposal.agenda_item
        if not agenda_item:
            return None

        return agenda_item.meeting

    def lock_info(self):
        lock_info = self.info.lock_info()
        locks = self.context.wl_lockValues()
        if len(locks) == 0:
            return lock_info
        lock = locks[0]
        lock_info["owner"] = lock.getOwner().strip()
        return lock_info
