from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class Signatories(PersistentList):
    def serialize(self):
        return json_compatible([signatory.serialize() for signatory in self])


class Signatory(Persistent):
    def __init__(self, userid='', email=''):
        self.userid = userid
        self.email = email

    def serialize(self):
        return json_compatible({
            'userid': self.userid,
            'email': self.email,
        })
