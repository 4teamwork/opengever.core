from base64 import urlsafe_b64decode
from opengever.base.security import elevated_privileges
from opengever.wopi.token import validate_access_token
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from opengever.sign.sign import Signer
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.interface import alsoProvides
import plone.protect.interfaces


class SignDocumentPost(Service):

    def reply(self):
        if not self.context.is_final_document() and not self.context.is_finalize_allowed():
            raise BadRequest(u'Document not finalizable')

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        Signer(self.context).start_signing()

        self.request.response.setStatus(200)

        return super(SignDocumentPost, self).reply()


class SignStatusPatch(Service):

    def check_permission(self):
        return

    def reply(self):
        body = json_body(self.request)
        state = body.get('state')
        token = body.get('token')
        if not state:
            raise BadRequest('state is required')

        signer = Signer(self.context)
        userid = signer.validate_access_token(token)
        if not userid:
            raise Unauthorized

        with elevated_privileges(user_id=userid):
            signer.update_signing_state(token, state)


class AddSignedVersionPost(Service):

    def check_permission(self):
        return

    def reply(self):
        body = json_body(self.request)
        _file = body.get('file')
        token = body.get('token')
        if not _file:
            raise BadRequest('state is required')

        signer = Signer(self.context)
        userid = signer.validate_access_token(token)
        if not userid:
            raise Unauthorized

        with elevated_privileges(user_id=userid):
            signer.update_signing_state(token, state)
