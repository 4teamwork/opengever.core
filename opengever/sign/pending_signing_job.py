from datetime import datetime
from opengever.sign.pending_editor import PendingEditors
from opengever.sign.pending_signer import PendingSigners
from opengever.sign.signed_version import SignedVersion
from persistent import Persistent
from plone.restapi.serializer.converters import json_compatible


class PendingSigningJob(Persistent):

    def __init__(self,
                 created=None,
                 userid='',
                 version=0,
                 signers=list(),
                 editors=list(),
                 job_id='',
                 redirect_url='',
                 invite_url='',
                 ):

        self.created = created or datetime.now()
        self.userid = userid
        self.version = version
        self.signers = PendingSigners.from_emails(signers)
        self.editors = PendingEditors.from_emails(editors)
        self.job_id = job_id
        self.redirect_url = redirect_url
        self.invite_url = invite_url

    def serialize(self):
        return json_compatible({
            'created': self.created,
            'userid': self.userid,
            'job_id': self.job_id,
            'redirect_url': self.redirect_url,
            'invite_url': self.invite_url,
            'signers': self.signers.serialize(),
            'editors': self.editors.serialize(),
            'version': self.version,
        })

    def to_signed_version(self):
        return SignedVersion(
            signatories=self.signers.to_signatories(),
            version=self.version + 1
        )
