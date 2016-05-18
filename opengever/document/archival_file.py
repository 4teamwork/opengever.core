from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.document.behaviors.metadata import IDocumentMetadata
from plone.namedfile.file import NamedBlobFile
import os


class ArchivalFileConverter(object):

    def __init__(self, document):
        self.document = document

    def trigger_conversion(self):
        IBumblebeeServiceV3(self.document).queue_conversion(
            PROCESSING_QUEUE, self.get_callback_url(), target_format='pdf/a')

    def get_callback_url(self):
        return "{}/archival_file_conversion_callback".format(
            self.document.absolute_url())

    def store_file(self, data):
        IDocumentMetadata(self.document).archival_file = NamedBlobFile(
            data=data,
            contentType='application/pdf',
            filename=self.get_file_name())

    def get_file_name(self):
        filename, ext = os.path.splitext(self.document.file.filename)
        return u'{}.pdf'.format(filename)
