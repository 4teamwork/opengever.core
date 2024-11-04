# from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
# from opengever.base.security import as_internal_workflow_transition
# from opengever.document.document import Document
# from opengever.sign.client import SignServiceClient
# from opengever.sign.storage import MetadataStorage
# from opengever.sign.token import TokenManager
# from plone import api
# from plone.dexterity.utils import safe_utf8
from requests.exceptions import ConnectionError


class Signer(object):
    """Provides all necessary methods to sign an objects through an external
    service.
    """

    def __init__(self, context):
        self.context = context
        # self.token_manager = TokenManager(context)
        # self.metadata_storage = MetadataStorage(context)

    def issue_token(self):
        return urlsafe_b64encode(self.token_manager.issue_token())

    def validate_token(self, token):
        pass
        # return self.token_manager.validate_token(urlsafe_b64decode(safe_utf8(token)))

    def invalidate_token(self):
        pass
        # self.token_manager.invalidate_token()

    def start_signing(self, signers):
        token = self.issue_token()
        # response = SignServiceClient().queue_signing(self.context, token, signers)
        # response = response.json()
        # self.metadata_storage.store(
        #     userid=api.user.get_current().id,
        #     version=self.context.get_current_version_id(missing_as_zero=True),
        #     signers=signers,
        #     job_id=response.get('id'),
        #     redirect_url=response.get('redirect_url'),
        # )
        return token

    def complete_signing(self, signed_pdf_data):
        pass
        # with as_internal_workflow_transition():
        #     api.content.transition(
        #         obj=self.context,
        #         transition=Document.signing_signed_transition,
        #         transition_params={'filedata': signed_pdf_data})

    def abort_signing(self):
        self.invalidate_token()
        # signing_data = self.metadata_storage.read()
        try:
            # SignServiceClient().abort_signing('123')
            pass
        except ConnectionError:
            # The user should always be able to abort the job
            pass

        self.clear_metadata()

    def clear_metadata(self):
        pass
        # self.metadata_storage.clear()

    def adopt_issuer(self):
        pass
        # userid = self.metadata_storage.read().get('userid')
        # user = api.user.get(userid=userid)
        # if not user:
        #     raise IssuerNotFound()
        # return api.env.adopt_user(user=user)

    def serialize(self):
        pass
        # return self.metadata_storage.read()


class IssuerNotFound(Exception):
    """Sign issuer not found.
    """
