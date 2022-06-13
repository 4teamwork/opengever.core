from opengever.base.behaviors.utils import set_attachment_content_disposition
import json


OCM_MIMETYPE = 'application/x-officeconnector'
OCM_FILE_EXTENSION = 'ocm'


class OCMFile(object):
    """File that encapsulates the data needed by the OfficeConnecor desktop
    helper application.

    These files will replace *.zem files in the near future. Currently only
    used for officeatwork integration though.

    Some of the code in this class has been heavily inspired by
    Producs.ExternalEditor.

    """
    ACTION_OFFICEATWORK = 'officeatwork'

    @classmethod
    def for_officeatwork(cls, document):
        """Return an ocm file for officeatwork, or None if no file could be
        created for the document.
        """

        if not document.is_shadow_document():
            return None

        return cls(document, cls.ACTION_OFFICEATWORK)

    def __init__(self, document, action):
        self.document = document
        self.request = self.document.REQUEST
        self.response = self.request.response
        self.action = action

    def get_data(self):
        data = {}
        data['action'] = self.action
        data['cookie'] = self.request.environ.get('HTTP_COOKIE', '')
        data['document'] = self._get_document_data()
        self._append_auth_information(data)

        return data

    def _append_auth_information(self, data):
        if self.request._auth:
            if self.request._auth[-1] == '\n':
                auth = self.request._auth[:-1]
            else:
                auth = self.request._auth

            data['auth'] = auth

    def _get_document_data(self):
        return {
            "title": self.document.title,
            "url": self.document.absolute_url(),
            "metadata": self._get_document_metadata()
        }

    def _get_document_metadata(self):
        return {}

    def _prepare_response(self):
        self.response.setHeader('X-Theme-Disabled', 'True')
        self.response.setHeader('Content-type', OCM_MIMETYPE)
        filename = '{}.{}'.format(self.document.getId(), OCM_FILE_EXTENSION)
        set_attachment_content_disposition(
            self.request, filename=filename, file=None)

    def dump(self):
        self._prepare_response()
        return json.dumps(self.get_data())
