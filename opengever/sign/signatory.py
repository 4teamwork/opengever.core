from plone.restapi.serializer.converters import json_compatible


class Signatories(list):

    def __eq__(self, value):
        return isinstance(value, Signatories) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, values):
        if not values:
            return cls()

        return cls([Signatory.from_json_object(value) for value in values])

    def to_json_object(self):
        return [signatory.to_json_object() for signatory in self]

    def serialize(self):
        return json_compatible([signatory.serialize() for signatory in self])


class Signatory(object):
    def __init__(self, userid='', email='', signed_at=None):
        self.userid = userid
        self.email = email
        self.signed_at = signed_at

    def __eq__(self, value):
        return isinstance(value, Signatory) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, value):
        return cls(
            userid=value.get('userid'),
            email=value.get('email'),
            signed_at=value.get('signed_at')
        )

    def to_json_object(self):
        return {
            'userid': self.userid,
            'email': self.email,
            'signed_at': self.signed_at,
        }

    def serialize(self):
        return json_compatible({
            'userid': self.userid,
            'email': self.email,
            'signed_at': self.signed_at,
        })
