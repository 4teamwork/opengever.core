from zope.annotation import IAnnotations


class PendingSigningJobStorage(object):
    """Responsible for storing metadata for a currently running sign process.
    """

    ANNOTATIONS_KEY = 'opengever.sign.pending_signing_job'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def store(self, pending_signing_job):
        self.annotations[self.ANNOTATIONS_KEY] = pending_signing_job

    def load(self):
        return self.annotations.get(self.ANNOTATIONS_KEY)

    def clear(self):
        if self.ANNOTATIONS_KEY in self.annotations:
            del self.annotations[self.ANNOTATIONS_KEY]
