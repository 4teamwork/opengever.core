from opengever.sign.utils import email_to_userid
from persistent import Persistent
from persistent.list import PersistentList
from plone.restapi.serializer.converters import json_compatible


class PendingEditors(PersistentList):
    def serialize(self):
        return json_compatible([pending_editor.serialize() for pending_editor in self])


class PendingEditor(Persistent):
    def __init__(self, email=''):
        self.email = email

    def serialize(self):
        return json_compatible({
            'userid': email_to_userid(self.email),
            'email': self.email,
        })
