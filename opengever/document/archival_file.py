from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.document.behaviors.metadata import IDocumentMetadata
from plone.namedfile.file import NamedBlobFile
import os


ARCHIVAL_FILE_STATE_CONVERTING = 1
ARCHIVAL_FILE_STATE_CONVERTED = 2
ARCHIVAL_FILE_STATE_MANUALLY = 3
ARCHIVAL_FILE_STATE_FAILED = 4


class ArchivalFileConverter(object):

    def __init__(self, document):
        self.document = document

    def trigger_conversion(self):
        self.set_state(ARCHIVAL_FILE_STATE_CONVERTING)
        IBumblebeeServiceV3(self.document).queue_conversion(
            PROCESSING_QUEUE, self.get_callback_url(), target_format='pdf/a')

    def set_state(self, state):
        IDocumentMetadata(self.document).archival_file_state = state

    def get_callback_url(self):
        return "{}/archival_file_conversion_callback".format(
            self.document.absolute_url())

    def store_file(self, data):
        IDocumentMetadata(self.document).archival_file = NamedBlobFile(
            data=data,
            contentType='application/pdf',
            filename=self.get_file_name())
        self.set_state(ARCHIVAL_FILE_STATE_CONVERTED)

    def handle_conversion_failure(self):
        self.set_state(ARCHIVAL_FILE_STATE_FAILED)

    def get_file_name(self):
        filename, ext = os.path.splitext(self.document.file.filename)
        return u'{}.pdf'.format(filename)
