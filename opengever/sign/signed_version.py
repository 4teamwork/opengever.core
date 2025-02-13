from datetime import datetime
from opengever.sign.signatory import Signatories
from plone.restapi.serializer.converters import json_compatible
from uuid import uuid4


class SignedVersions(dict):

    def __eq__(self, value):
        return isinstance(value, SignedVersions) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, values):
        if not values:
            return cls()

        return cls({
            key: SignedVersion.from_json_object(value) for key, value in values.items()
        })

    def to_json_object(self):
        return {
            version_id: version_item.to_json_object() for version_id, version_item in self.items()
        }

    def add_signed_version(self, signed_version):
        if signed_version.version in self:
            raise Exception("Signed version %s already exists" % signed_version.version)

        self[signed_version.version] = signed_version

    def serialize(self):
        return json_compatible(
            {
                version_id: version_item.serialize() for version_id, version_item in self.items()
            })


class SignedVersion(object):
    def __init__(self,
                 id_=None,
                 created=None,
                 signatories=Signatories(),
                 version=0,
                 ):

        if not isinstance(signatories, Signatories):
            raise TypeError(
                "Expected 'signatories' to be of type Signatories - "
                "got %r instead" % signatories)

        self.id_ = id_ or str(uuid4())
        self.created = created or datetime.now()
        self.version = version
        self.signatories = signatories

    def __eq__(self, value):
        return isinstance(value, SignedVersion) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, value):
        return cls(
            id_=value.get('id'),
            created=value.get('created'),
            signatories=Signatories.from_json_object(value.get('signatories')),
            version=value.get('version')
        )

    def to_json_object(self):
        return {
            'id': self.id_,
            'created': self.created,
            'signatories': self.signatories.to_json_object(),
            'version': self.version,
        }

    def serialize(self):
        return json_compatible({
            'id': self.id_,
            'created': self.created,
            'signatories': self.signatories.serialize(),
            'version': self.version,
        })
