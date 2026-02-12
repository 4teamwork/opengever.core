from opengever.sign.pending_signing_job import PendingSigningJob
from opengever.sign.signed_version import SignedVersions
from zope.annotation import IAnnotations


class PendingSigningJobStorage(object):
    """Responsible for storing metadata for a currently running sign process.
    """

    ANNOTATIONS_KEY = 'opengever.sign.pending_signing_job'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def store(self, pending_signing_job):
        self.annotations[self.ANNOTATIONS_KEY] = pending_signing_job.to_json_object()

    def load(self):
        return PendingSigningJob.from_json_object(self.annotations.get(self.ANNOTATIONS_KEY))

    def clear(self):
        if self.ANNOTATIONS_KEY in self.annotations:
            del self.annotations[self.ANNOTATIONS_KEY]


class SignedVersionsStorage(object):
    """Storage for signed versions.
    """

    ANNOTATIONS_KEY = 'opengever.sign.signed_versions'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def load(self, auto_init=True):
        if auto_init and self.ANNOTATIONS_KEY not in self.annotations:
            self.store(SignedVersions())
        return SignedVersions.from_json_object(self.annotations.get(self.ANNOTATIONS_KEY))

    def store(self, signed_versions):
        self.annotations[self.ANNOTATIONS_KEY] = signed_versions.to_json_object()

    def clear(self):
        if self.ANNOTATIONS_KEY in self.annotations:
            del self.annotations[self.ANNOTATIONS_KEY]
