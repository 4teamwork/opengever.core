from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.sign.utils import email_to_userid
from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class PendingSigners(PersistentList):

    @classmethod
    def from_emails(cls, emails):
        return cls([PendingSigner(email=email) for email in emails])

    def serialize(self):
        return json_compatible([pending_signer.serialize() for pending_signer in self])

    def to_signatories(self):
        return Signatories([pending_signer.to_signatory() for pending_signer in self])


class PendingSigner(Persistent):
    def __init__(self,
                 userid='',
                 email='',
                 ):

        self.userid = userid
        self.email = email

    def serialize(self):
        return json_compatible({
            'userid': self.resolved_userid(),
            'email': self.email,
        })

    def resolved_userid(self):
        return self.userid if self.userid else email_to_userid(self.email)

    def to_signatory(self):
        return Signatory(userid=self.resolved_userid(),
                         email=self.email)
