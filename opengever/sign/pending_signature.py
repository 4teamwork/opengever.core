from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.sign.utils import email_to_userid
from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class PendingSignatures(PersistentList):

    def serialize(self):
        return json_compatible([signature.serialize() for signature in self])

    def to_signatories(self):
        return Signatories([signature.to_signatory() for signature in self])


class PendingSignature(Persistent):

    def __init__(self,
                 email='',
                 status='',
                 signed_at='',
                 ):

        self.email = email
        self.status = status
        self.signed_at = signed_at

    def serialize(self):
        return json_compatible({
            'userid': self.resolved_userid(),
            'email': self.email,
            'status': self.status,
            'signed_at': self.signed_at,
        })

    def resolved_userid(self):
        return email_to_userid(self.email)

    def to_signatory(self):
        return Signatory(userid=self.resolved_userid(),
                         email=self.email)
