from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from opengever.base.security import as_internal_workflow_transition
from opengever.document.document import Document
from opengever.sign.client import sign_service_client
from opengever.sign.pending_signing_job import PendingSigningJob
from opengever.sign.storage import PendingSigningJobStorage
from opengever.sign.storage import SignedVersionsStorage
from opengever.sign.token import TokenManager
from plone import api
from plone.dexterity.utils import safe_utf8
from requests.exceptions import ConnectionError


class Signer(object):
    """Provides all necessary methods to sign an objects through an external
    service.
    """

    def __init__(self, context):
        self.context = context
        self.token_manager = TokenManager(context)
        self.pending_signing_job_storage = PendingSigningJobStorage(context)
        self.signed_versions_storage = SignedVersionsStorage(context)

    def issue_token(self):
        return urlsafe_b64encode(self.token_manager.issue_token())

    def validate_token(self, token):
        return self.token_manager.validate_token(urlsafe_b64decode(safe_utf8(token)))

    def invalidate_token(self):
        self.token_manager.invalidate_token()

    def start_signing(self, signers=[], editors=[]):
        token = self.issue_token()
        response = sign_service_client.queue_signing(self.context, token,
                                                     signers, editors)
        self.pending_signing_job = PendingSigningJob(
            userid=api.user.get_current().id,
            version=self.context.get_current_version_id(missing_as_zero=True),
            signers=signers,
            editors=editors,
            job_id=response.get('id'),
            redirect_url=response.get('redirect_url'),
            invite_url=response.get('invite_url'),
        )
        return token

    def complete_signing(self, signed_pdf_data):
        with as_internal_workflow_transition():
            api.content.transition(
                obj=self.context,
                transition=Document.signing_signed_transition,
                transition_params={'filedata': signed_pdf_data})

    def finish_signing(self):
        signed_version = self.pending_signing_job.to_signed_version()
        self.signed_versions_storage.load().add_signed_version(signed_version)
        self.pending_signing_job_storage.clear()

    @property
    def pending_signing_job(self):
        return self.pending_signing_job_storage.load()

    @pending_signing_job.setter
    def pending_signing_job(self, pending_signing_job):
        self.pending_signing_job_storage.store(pending_signing_job)

    def abort_signing(self):
        self.invalidate_token()
        self.abort_pending_signing_job(self.pending_signing_job)
        self.pending_signing_job_storage.clear()

    def abort_pending_signing_job(self, pending_signing_job):
        if not pending_signing_job:
            return

        try:
            sign_service_client.abort_signing(pending_signing_job.job_id)
        except ConnectionError:
            # The user should always be able to abort the job
            pass

    def adopt_issuer(self):
        user = api.user.get(userid=self.pending_signing_job.userid)
        if not user:
            raise IssuerNotFound()
        return api.env.adopt_user(user=user)

    def serialize_pending_signing_job(self):
        return self.pending_signing_job.serialize() if self.pending_signing_job else {}

    def serialize_signed_versions(self):
        return self.signed_versions_storage.load().serialize()


class IssuerNotFound(Exception):
    """Signing issuer not found.
    """
