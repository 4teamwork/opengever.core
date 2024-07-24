from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from opengever.sign.sign import Signer
from zExceptions import BadRequest
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
