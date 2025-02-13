from datetime import datetime
from opengever.sign.pending_editor import PendingEditors
from opengever.sign.pending_signature import PendingSignatures
from opengever.sign.signed_version import SignedVersion
from plone.restapi.serializer.converters import json_compatible


class PendingSigningJob(object):

    def __init__(self,
                 created=None,
                 userid='',
                 version=0,
                 editors=list(),
                 signatures=None,
                 job_id='',
                 redirect_url='',
                 invite_url='',
                 ):

        self.created = created or datetime.now()
        self.userid = userid
        self.version = version
        self.editors = editors if isinstance(
            editors, PendingEditors) else PendingEditors.from_emails(editors)
        self.signatures = PendingSignatures() if signatures is None else signatures
        self.job_id = job_id
        self.redirect_url = redirect_url
        self.invite_url = invite_url

    def __eq__(self, value):
        return isinstance(value, PendingSigningJob) and value.to_json_object() == self.to_json_object()

    def __ne__(self, value):
        return not value == self

    @classmethod
    def from_json_object(cls, value):
        if not value:
            return None

        return cls(
            created=value.get('created'),
            userid=value.get('userid'),
            version=value.get('version'),
            editors=PendingEditors.from_json_object(value.get('editors', [])),
            signatures=PendingSignatures.from_json_object(value.get('signatures')),
            job_id=value.get('job_id'),
            redirect_url=value.get('redirect_url'),
            invite_url=value.get('invite_url'),
        )

    def to_json_object(self):
        return {
            'created': self.created,
            'userid': self.userid,
            'job_id': self.job_id,
            'redirect_url': self.redirect_url,
            'invite_url': self.invite_url,
            'editors': self.editors.to_json_object(),
            'signatures': self.signatures.to_json_object(),
            'version': self.version,
        }

    def serialize(self):
        return json_compatible({
            'created': self.created,
            'userid': self.userid,
            'job_id': self.job_id,
            'redirect_url': self.redirect_url,
            'invite_url': self.invite_url,
            'editors': self.editors.serialize(),
            'signatures': self.signatures.serialize(),
            'version': self.version,
        })

    def to_signed_version(self):
        return SignedVersion(
            signatories=self.signatures.to_signatories(),
            version=self.version + 1
        )

    def update(self, **data):
        editors = data.get('editors')
        if isinstance(editors, list):
            self.editors = PendingEditors.from_emails(editors)

        signatures = data.get('signatures')
        if isinstance(signatures, PendingSignatures):
            self.signatures = signatures

        return self
