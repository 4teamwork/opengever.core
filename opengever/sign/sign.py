import os
from plone import api
from persistent.dict import PersistentDict
from plone.namedfile.file import NamedBlobFile
from zope.annotation import IAnnotations
from opengever.wopi.token import create_access_token
from opengever.wopi.token import validate_access_token
from opengever.sign.client import SignServiceClient
from plone.uuid.interfaces import IUUID
from datetime import datetime
from opengever.document.document import Document
from zExceptions import Unauthorized
from zExceptions import NotFound
from opengever.document.versioner import Versioner
from opengever.sign import _


class SignStorage(object):

    key = 'signings_storages'

    def __init__(self, context):
        self.context = context

    def add(self, userid, token, state='pending'):
        annotations = IAnnotations(self.context)
        if self.key not in annotations:
            annotations[self.key] = PersistentDict()

        annotations[self.key][token] = {
            'userid': userid,
            'state': state,
            'created': datetime.now(),
        }

    def get(self, token):
        storage = IAnnotations(self.context).get(self.key, {})
        return storage.get(token)

    def items(self):
        annotations = IAnnotations(self.context)
        return annotations.get(self.key, {}).items()


class Signer(object):

    def __init__(self, context):
        self.context = context
        self.storage = SignStorage(context)

    def start_signing(self):
        if api.content.get_state(self.context) != Document.final_state:
            api.content.transition(
                obj=self.context, transition=Document.finalize_transition)

        token = self.register_signing()
        SignServiceClient().queue_signing(self.context, token)

        return token

    def register_signing(self):
        userid = api.user.get_current().id
        token = create_access_token(userid, IUUID(self.context))
        self.storage.add(userid, token)
        return token

    def update_signing_state(self, token, state):
        if not validate_access_token(token,  IUUID(self.context)):
            raise Unauthorized

        item = self.storage.get(token)
        if not item:
            raise NotFound

        item['state'] = state

    def add_signed_version(self, token, filedata):
        if not validate_access_token(token,  IUUID(self.context)):
            raise Unauthorized

        item = self.storage.get(token)
        if not item:
            raise NotFound

        self.context.file = NamedBlobFile(
            data=filedata,
            contentType=u'application/pdf',
            filename=self.get_file_name())

        Versioner(self.context).create_version(
            _(u'label_document_signed', default=u'Document signed'))

        item['state'] = u'signed'

    def get_file_name(self):
        filename, ext = os.path.splitext(self.context.get_filename())
        return u'{}.pdf'.format(filename)
