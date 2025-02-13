from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class Signatories(PersistentList):
    def serialize(self):
        return json_compatible([signatory.serialize() for signatory in self])


class Signatory(Persistent):
    def __init__(self, userid='', email='', signed_at=None):
        self.userid = userid
        self.email = email
        self.signed_at = signed_at

    def serialize(self):
        return json_compatible({
            'userid': self.userid,
            'email': self.email,
            'signed_at': self.signed_at,
        })
