from datetime import datetime
from opengever.sign.pending_signer import PendingSigner
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
                 job_id='',
                 redirect_url='',
                 ):

        self.created = created or datetime.now()
        self.userid = userid
        self.version = version
        self.signers = PendingSigners([PendingSigner(email=signer) for signer in signers])
        self.job_id = job_id
        self.redirect_url = redirect_url

    def serialize(self):
        return json_compatible({
            'created': self.created,
            'userid': self.userid,
            'job_id': self.job_id,
            'redirect_url': self.redirect_url,
            'signers': self.signers.serialize(),
            'version': self.version,
        })

    def to_signed_version(self):
        return SignedVersion(
            signatories=self.signers.to_signatories(),
            version=self.version + 1
        )
