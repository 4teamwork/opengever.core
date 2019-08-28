from ftw.bumblebee.config import bumblebee_config
from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeServiceV3
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.interfaces import IDossierResolveProperties
from plone import api
from plone.namedfile.file import NamedBlobFile
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.globalrequest import getRequest
import os


STATE_CONVERTING = 1
STATE_CONVERTED = 2
STATE_MANUALLY_PROVIDED = 3
STATE_FAILED_TEMPORARILY = 4
STATE_FAILED_PERMANENTLY = 5

ARCHIVAL_FILE_STATE_MAPPING = {
    1: "STATE_CONVERTING",
    2: "STATE_CONVERTED",
    3: "STATE_MANUALLY_PROVIDED",
    4: "STATE_FAILED_TEMPORARILY",
    5: "STATE_FAILED_PERMANENTLY",
}

ARCHIVAL_FILE_CONVERSION_QUEUE_KEY = 'opengever.document.\
                                      archival_file_conversion_queue_annotations_key'


class ArchivalFileConverter(object):

    def __init__(self, document):
        self.document = document
        self.document_intid = getUtility(IIntIds).getId(self.document)

    def trigger_conversion(self):
        if self.is_mimetype_blacklisted():
            self.set_state(STATE_FAILED_PERMANENTLY)
            return

        if self.get_state() == STATE_MANUALLY_PROVIDED:
            return

        if self.is_already_queued():
            return

        self.queue_conversion()

    def is_mimetype_blacklisted(self):
        black_listed_types = api.portal.get_registry_record(
            name='archival_file_conversion_blacklist',
            interface=IDossierResolveProperties)

        if not black_listed_types:
            return False

        return self.document.get_file().contentType in black_listed_types

    def queue_conversion(self):
        self.set_state(STATE_CONVERTING)
        IBumblebeeServiceV3(getRequest()).queue_conversion(
            self.document, PROCESSING_QUEUE,
            self.get_callback_url(), target_format='pdf/a')

        annotations = IAnnotations(getRequest())
        if ARCHIVAL_FILE_CONVERSION_QUEUE_KEY not in annotations:
            annotations[ARCHIVAL_FILE_CONVERSION_QUEUE_KEY] = []
        annotations[ARCHIVAL_FILE_CONVERSION_QUEUE_KEY].append(self.document_intid)

    def is_already_queued(self):
        """ Check whether the conversion has already been queued during this
        request
        """
        annotations = IAnnotations(getRequest())
        queued = annotations.get(ARCHIVAL_FILE_CONVERSION_QUEUE_KEY, [])
        return self.document_intid in queued

    def get_state(self):
        return IDocumentMetadata(self.document).archival_file_state

    def set_state(self, state):
        IDocumentMetadata(self.document).archival_file_state = state

    def remove_state(self):
        IDocumentMetadata(self.document).archival_file_state = None

    def get_callback_url(self):
        """Get the URL for the callback to upload the archival PDF to.

        This URL must be accessible by bumblebee, so we must not use the
        virtual hosting based URL here, because that wouldn't work when
        using SSH tunnels or nightly jobs run via bin/instance.
        """
        base_url = bumblebee_config.internal_plone_url
        relative_path = '/'.join(self.document.getPhysicalPath()[2:])
        doc_url = '/'.join([base_url, relative_path])
        return "{}/archival_file_conversion_callback".format(doc_url)

    def store_file(self, data, mimetype='application/pdf'):
        if isinstance(mimetype, unicode):
            mimetype = mimetype.encode('utf-8')

        IDocumentMetadata(self.document).archival_file = NamedBlobFile(
            data=data,
            contentType=mimetype,
            filename=self.get_file_name())
        self.set_state(STATE_CONVERTED)

    def handle_temporary_conversion_failure(self):
        self.set_state(STATE_FAILED_TEMPORARILY)

    def handle_permanent_conversion_failure(self):
        self.set_state(STATE_FAILED_PERMANENTLY)

    def handle_manual_file_upload(self):
        self.set_state(STATE_MANUALLY_PROVIDED)

    def get_file_name(self):
        filename, ext = os.path.splitext(self.document.get_filename())
        return u'{}.pdf'.format(filename)
