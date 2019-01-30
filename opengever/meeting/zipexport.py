from BTrees.OOBTree import OOBTree
from datetime import timedelta
from ftw.bumblebee import get_service_v3
from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.zipexport.generation import ZipGenerator
from ftw.zipexport.utils import normalize_path
from logging import getLogger
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.security import elevated_privileges
from opengever.meeting import _
from opengever.meeting.traverser import MeetingDocumentWithFileTraverser
from persistent.mapping import PersistentMapping
from plone import api
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from StringIO import StringIO
from tzlocal import get_localzone
from zExceptions import BadRequest
from zope.annotation import IAnnotations
from zope.globalrequest import getRequest
from zope.i18n import translate
import json
import os
import uuid


logger = getLogger('opengever.meeting.zipexport')

ZIP_JOBS_KEY = 'opengever.meeting.zipexporter'
ZIP_EXPIRATION_DAYS = 2


def format_modified(modified):
    return safe_unicode(
        get_localzone().localize(
            modified.asdatetime().replace(tzinfo=None)
        ).isoformat())


class MeetingDocumentZipper(MeetingDocumentWithFileTraverser):

    def __init__(self, meeting, generator):
        super(MeetingDocumentZipper, self).__init__(meeting)
        self.generator = generator
        self.json_serializer = MeetingJSONSerializer(self.meeting, self)

    def get_zip_file(self):
        self.traverse()
        self.generator.add_file('meeting.json', self.get_meeting_json_file())
        return self.generator.generate()

    def get_filename(self, document):
        return normalize_path(document.get_filename())

    def get_file(self, document):
        return document.get_file()

    def get_agenda_item_filename(self, document, agenda_item_number):
        return normalize_path(u'{}/{}'.format(
            translate(
                _(u'title_agenda_item', default=u'Agenda item ${agenda_item_number}',
                  mapping={u'number': agenda_item_number}),
                context=getRequest(),
                ),
            safe_unicode(self.get_filename(document)))
        )

    def get_agenda_item_attachment_filename(self, document, agenda_item_number, attachment_number):
        return normalize_path(u'{}/{}/{}_{}'.format(
            translate(
                _(u'title_agenda_item', default=u'Agenda item ${agenda_item_number}',
                  mapping={u'number': agenda_item_number}),
                context=getRequest(),
                ),
            translate(
                _(u'attachments', default=u'Attachments'),
                context=getRequest(),
                ),
            str(attachment_number),
            safe_unicode(self.get_filename(document)))
        )

    def traverse_protocol_document(self, document):
        self.generator.add_file(
            self.get_filename(document), self.get_file(document).open()
        )

    def traverse_agenda_item_list_document(self, document):
        self.generator.add_file(
            self.get_filename(document), self.get_file(document).open()
        )

    def traverse_agenda_item_document(self, document, agenda_item):
        self.generator.add_file(
            self.get_agenda_item_filename(document, agenda_item.formatted_number),
            self.get_file(document).open()
        )

    def traverse_agenda_item_attachment(self, document, agenda_item, attachment_number):
        self.generator.add_file(
            self.get_agenda_item_attachment_filename(document, agenda_item.formatted_number, attachment_number),
            self.get_file(document).open()
        )

    def get_meeting_json_file(self):
        return StringIO(self.json_serializer.get_json())


class MeetingPDFDocumentZipper(MeetingDocumentZipper):
    """Zip a meetings documents, but replace documents with a PDF if available.

    if no PDF is available the original document will be used as a replacement.
    """
    def __init__(self, meeting, pdfs, generator):
        super(MeetingPDFDocumentZipper, self).__init__(meeting, generator)
        self.pdfs = pdfs

    def get_filename(self, document):
        document_id = IUUID(document)
        filename = super(MeetingPDFDocumentZipper, self).get_filename(document)
        if document_id not in self.pdfs:
            return filename

        return u'{}.pdf'.format(os.path.splitext(filename)[0])

    def get_file(self, document):
        document_id = IUUID(document)
        if document_id not in self.pdfs:
            logger.info('Falling back to original format for %r' % document)
            return super(MeetingPDFDocumentZipper, self).get_file(document)

        return self.pdfs[document_id]


class MeetingJSONSerializer(MeetingDocumentWithFileTraverser):
    """Represents a JSON file with which grimlock can import the meeting."""

    def __init__(self, meeting, zipper):
        super(MeetingJSONSerializer, self).__init__(meeting)
        self.zipper = zipper
        self.data = {
            'opengever_id': meeting.meeting_id,
            'title': safe_unicode(meeting.title),
            'start': safe_unicode(meeting.start.isoformat()),
            'end': safe_unicode(meeting.end.isoformat() if meeting.end else ''),
            'location': safe_unicode(meeting.location),
            'committee': {
                'oguid': safe_unicode(meeting.committee.oguid.id),
                'title': safe_unicode(meeting.committee.title),
            },
            'agenda_items': [],
        }

    def get_json(self):
        self.traverse()

        json_data = {
            'version': '1.0.0',
            'meetings': [self.data],
        }
        return json.dumps(json_data, sort_keys=True, indent=4)

    def traverse_protocol_document(self, document):
        self.data['protocol'] = {
            'checksum': IBumblebeeDocument(document).get_checksum(),
            'file': self.zipper.get_filename(document),
            'modified': format_modified(document.modified()),
        }

    def traverse_agenda_item(self, agenda_item):
        self.current_agenda_item_data = {
            'opengever_id': agenda_item.agenda_item_id,
            'title': safe_unicode(agenda_item.get_title()),
            'sort_order': agenda_item.sort_order,
        }

        super(MeetingJSONSerializer, self).traverse_agenda_item(agenda_item)

        self.data['agenda_items'].append(self.current_agenda_item_data)
        self.current_agenda_item_data = None

    def traverse_agenda_item_document(self, document, agenda_item):
        self.current_agenda_item_data['number'] = agenda_item.formatted_number
        self.current_agenda_item_data['number_raw'] = agenda_item.item_number
        self.current_agenda_item_data['proposal'] = {
            'checksum': IBumblebeeDocument(document).get_checksum(),
            'file': self.zipper.get_agenda_item_filename(document, agenda_item.formatted_number),
            'modified': format_modified(document.modified()),
        }

    def traverse_agenda_item_attachment(self, document, agenda_item, attachment_number):
        attachment_data = self.current_agenda_item_data.setdefault(
            'attachments', [])

        attachment_data.append({
            'checksum': IBumblebeeDocument(document).get_checksum(),
            'file': self.zipper.get_agenda_item_attachment_filename(
                document, agenda_item.formatted_number, attachment_number),
            'modified': format_modified(document.modified()),
            'title': safe_unicode(document.Title()),
        })


class ZipExportDocumentCollector(MeetingDocumentWithFileTraverser):
    """Collect all documents that will be exported in a zip."""

    def __init__(self, meeting):
        super(ZipExportDocumentCollector, self).__init__(meeting)
        self._documents = []

    def traverse_protocol_document(self, document):
        self._collect(document)

    def traverse_agenda_item_list_document(self, document):
        self._collect(document)

    def traverse_agenda_item_document(self, document, agenda_item):
        self._collect(document)

    def traverse_agenda_item_attachment(self, document, agenda_item, attachment_number):
        self._collect(document)

    def get_documents(self):
        self.traverse()
        return tuple(self._documents)

    def _collect(self, document):
        self._documents.append(document)


class ZipJob(object):
    """Encapsulates low-level data structures for Zip-generation jobs that
    use the Bumblebee 'demand' endpoint.
    """

    def __init__(self, zip_job_data):
        self._data = zip_job_data

    @property
    def job_id(self):
        return self._data['job_id']

    @property
    def timestamp(self):
        return self._data['timestamp']

    def get_doc_status(self, document_id):
        return self._data['documents'][document_id]

    def add_doc_status(self, document_id, status_data):
        doc_status = PersistentMapping()
        doc_status.update(status_data)
        self._data['documents'][document_id] = doc_status

    def update_doc_status(self, document_id, status_data):
        doc_status = self.get_doc_status(document_id)
        doc_status.update(status_data)

    def list_document_ids(self):
        return list(self._data['documents'].keys())

    def is_finished(self):
        return 'zip_file' in self._data

    def get_zip_file(self):
        return self._data['zip_file']

    def set_zip_file(self, zip_file_blob):
        self._data['zip_file'] = zip_file_blob

    def _get_doc_in_job_id(self, document):
        return '{}:{}'.format(self.job_id, IUUID(document))

    def get_progress(self):
        """Returns a dict describing progress of this job.
        """
        status = {
            'skipped': 0,
            'finished': 0,
            'converting': 0,
            'zipped': 0,
            'is_finished': self.is_finished(),
        }
        for document_info in self._data['documents'].values():
            status[document_info['status']] += 1
        return status

    def is_finished_converting(self):
        progress = self.get_progress()
        return progress['converting'] == 0


class ZipJobManager(object):
    """Manages ZIP jobs that use the Bumblebee demand endpoint.
    """

    def __init__(self, meeting):
        self.meeting = meeting
        self.committee = meeting.committee.oguid.resolve_object()

        self._zip_jobs = IAnnotations(self.committee).get(ZIP_JOBS_KEY, {})

    def get_job(self, job_id):
        return ZipJob(self._zip_jobs[job_id])

    def create_job(self):
        self._cleanup_old_jobs()
        self._prepare_committee_annotations()

        job_id = str(uuid.uuid4())

        zip_job_data = PersistentMapping()
        zip_job_data['job_id'] = job_id
        zip_job_data['timestamp'] = utcnow_tz_aware()
        zip_job_data['documents'] = OOBTree()

        self._zip_jobs[job_id] = zip_job_data

        return ZipJob(zip_job_data)

    def remove_job(self, job_id):
        del self._zip_jobs[job_id]

    def _prepare_committee_annotations(self):
        annotations = IAnnotations(self.committee)
        if ZIP_JOBS_KEY not in annotations:
            annotations[ZIP_JOBS_KEY] = OOBTree()
        self._zip_jobs = annotations[ZIP_JOBS_KEY]

    def _cleanup_old_jobs(self):
        """Remove expired zip jobs.

        The zip jobs are only kept for a relatively short amount of time as
        they are a temporary thing.
        """
        to_remove = set()
        now = utcnow_tz_aware()
        expiration_delta = timedelta(days=ZIP_EXPIRATION_DAYS)

        for zip_job_data in self._zip_jobs.values():
            delta = now - zip_job_data['timestamp']
            if delta > expiration_delta:
                to_remove.add(zip_job_data['job_id'])

        for job_id in to_remove:
            self.remove_job(job_id)


class MeetingZipExporter(object):
    """Exports a meeting's documents as PDF in a zip file.

    Requests pdfs from bumblebee, if available. Falls back to original file
    if no pdf can be supplied or pdf conversion was skipped/erroneous.
    """

    def __init__(self, meeting, job_id=None):
        self.meeting = meeting
        self.committee = meeting.committee.oguid.resolve_object()
        self.catalog = api.portal.get_tool('portal_catalog')

        self.job_manager = ZipJobManager(self.meeting)
        self.zip_job = None

        if job_id is not None:
            self.zip_job = self.job_manager.get_job(job_id)

    def demand_pdfs(self):
        """Demand pdfs for all zip documents from bumlebee."""
        self.zip_job = self.job_manager.create_job()

        for document in self._collect_meeting_documents():
            status = self._queue_demand_job(document)
            self.zip_job.add_doc_status(IUUID(document), {'status': status})

        return self.zip_job

    def resolve_document(self, doc_in_job_id):
        document_id = self.extract_document_id(doc_in_job_id)

        if document_id not in self.zip_job.list_document_ids():
            raise BadRequest(
                'Document with UUID {} not found in job {}'.format(
                    document_id, self.zip_job.job_id))

        # Need to do an unrestricted query because the 'receive_meeting_zip_pdf'
        # view which uses this method will be called (by Bumblebee) with an
        # Anonymous user context.
        brain = self.catalog.unrestrictedSearchResults(UID=document_id)[0]
        document = brain._unrestrictedGetObject()
        return document

    def receive_pdf(self, doc_in_job_id, mimetype, data):
        document_id = self.extract_document_id(doc_in_job_id)
        self._update_job_with_pdf(document_id, mimetype, data)

    def _update_job_with_pdf(self, document_id, mimetype, data):
        # we're using NamedBlobFile here to re-use an IStorage adapter, the
        # filename is not relevant
        blob_file = NamedBlobFile(data=data, contentType=mimetype)
        self.zip_job.update_doc_status(document_id, {
            'status': 'finished',
            'blob': blob_file,
        })

    def generate_zipfile(self):
        # we might be called when the zip file has already been generated.
        # abort in such cases.
        if self.zip_job.is_finished():
            return

        pdfs = {}
        for document_id in self.zip_job.list_document_ids():
            doc_status = self.zip_job.get_doc_status(document_id)
            if doc_status['status'] == 'finished':
                pdfs[document_id] = doc_status.pop('blob')
                doc_status['status'] = 'zipped'

        with ZipGenerator() as generator, elevated_privileges():
            zipper = MeetingPDFDocumentZipper(
                self.meeting, pdfs, generator)

            zip_blob_file = NamedBlobFile(data=zipper.get_zip_file(),
                                          contentType='application/zip')
            self.zip_job.set_zip_file(zip_blob_file)

    def mark_as_skipped(self, doc_in_job_id):
        document_id = self.extract_document_id(doc_in_job_id)
        self.zip_job.update_doc_status(document_id, {'status': 'skipped'})

    def is_finished_converting(self):
        return self.zip_job.is_finished_converting()

    def _queue_demand_job(self, document):
        callback_url = self.meeting.get_url(view='receive_meeting_zip_pdf')
        doc_in_job_id = self.zip_job._get_doc_in_job_id(document)

        if get_service_v3().queue_demand(
                document, PROCESSING_QUEUE, callback_url,
                opaque_id=doc_in_job_id):
            return 'converting'
        else:
            return 'skipped'

    @staticmethod
    def extract_job_id(doc_in_job_id):
        return doc_in_job_id.split(':')[0]

    @staticmethod
    def extract_document_id(doc_in_job_id):
        return doc_in_job_id.split(':')[1]

    def _collect_meeting_documents(self):
        return ZipExportDocumentCollector(self.meeting).get_documents()
