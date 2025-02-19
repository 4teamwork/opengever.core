from opengever.sign.utils import email_to_userid
from plone.restapi.serializer.converters import json_compatible


class PendingEditors(list):

    @classmethod
    def from_emails(cls, emails):
        return cls([PendingEditor(email=email) for email in emails])

    @classmethod
    def from_json_object(cls, values):
        if not values:
            return cls()

        return cls(
            [PendingEditor.from_json_object(value) for value in values])

    def to_json_object(self):
        return [pending_editor.to_json_object() for pending_editor in self]

    def __eq__(self, value):
        return isinstance(value, PendingEditors) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    def serialize(self):
        return json_compatible([pending_editor.serialize() for pending_editor in self])


class PendingEditor(object):
    def __init__(self, email=''):
        self.email = email

    def __eq__(self, value):
        return isinstance(value, PendingEditor) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, value):
        return cls(
            email=value.get('email')
        )

    def to_json_object(self):
        return {
            'email': self.email
        }

    def serialize(self):
        return json_compatible({
            'userid': email_to_userid(self.email),
            'email': self.email,
        })
