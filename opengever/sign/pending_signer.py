from opengever.sign.utils import email_to_userid
from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class PendingSigners(PersistentList):
    def serialize(self):
        return json_compatible([pending_signer.serialize() for pending_signer in self])


class PendingSigner(Persistent):
    def __init__(self,
                 userid='',
                 email='',
                 ):

        self.userid = userid
        self.email = email

    def serialize(self):
        return json_compatible({
            'userid': self.userid if self.userid else email_to_userid(self.email),
            'email': self.email,
        })
