from datetime import datetime
from opengever.base.utils import make_persistent
from zope.annotation import IAnnotations


class MetadataStorage(object):
    """Responsible for storing metadata for a currently running sign process.
    """

    ANNOTATIONS_KEY = 'sign_data'

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def store(self, userid, version, signers, job_id, redirect_url):
        self._set_data({
            'created': datetime.now(),
            'userid': userid,
            'job_id': job_id,
            'redirect_url': redirect_url,
            'signers': signers,
            'version': version,
        })

    def read(self):
        return self._get_data()

    def clear(self):
        self._set_data({})

    def _set_data(self, data):
        self.annotations[self.ANNOTATIONS_KEY] = make_persistent(data)

    def _get_data(self):
        return dict(self.annotations.get(self.ANNOTATIONS_KEY, {}))
