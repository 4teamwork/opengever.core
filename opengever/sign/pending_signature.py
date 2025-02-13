from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.sign.utils import email_to_userid
from plone.restapi.serializer.converters import json_compatible


class PendingSignatures(list):

    def __eq__(self, value):
        return isinstance(value, PendingSignatures) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, values):
        if not values:
            return cls()

        return cls([PendingSignature.from_json_object(value) for value in values])

    def to_json_object(self):
        return [signature.to_json_object() for signature in self]

    def serialize(self):
        return json_compatible([signature.serialize() for signature in self])

    def to_signatories(self):
        return Signatories([signature.to_signatory() for signature in self])


class PendingSignature(object):

    def __init__(self,
                 email='',
                 status='',
                 signed_at='',
                 ):

        self.email = email
        self.status = status
        self.signed_at = signed_at

    def __eq__(self, value):
        return isinstance(value, PendingSignature) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, value):
        return cls(
            email=value.get('email'),
            status=value.get('status'),
            signed_at=value.get('signed_at')
        )

    def to_json_object(self):
        return {
            'email': self.email,
            'status': self.status,
            'signed_at': self.signed_at,
        }

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
                         email=self.email,
                         signed_at=self.signed_at)
