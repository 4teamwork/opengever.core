from datetime import datetime
from opengever.sign.signatory import Signatories
from persistent import Persistent
from persistent.dict import PersistentDict
from plone.restapi.serializer.converters import json_compatible
from uuid import uuid4


class SignedVersions(PersistentDict):
    def add_signed_version(self, signed_version):
        if signed_version.version in self:
            raise Exception("Signed version %s already exists" % signed_version.version)

        self[signed_version.version] = signed_version

    def serialize(self):
        return json_compatible(
            {
                version_id: version_item.serialize() for version_id, version_item in self.items()
            })


class SignedVersion(Persistent):
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

    def serialize(self):
        return json_compatible({
            'id': self.id_,
            'created': self.created,
            'signatories': self.signatories.serialize(),
            'version': self.version,
        })
