from BTrees.OOBTree import OOBTree
from datetime import timedelta
from ftw.bumblebee import get_service_v3
from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.zipexport.utils import normalize_path
from opengever.base.date_time import utcnow_tz_aware
from opengever.meeting import _
from opengever.meeting.traverser import MeetingTraverser
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.utils import safe_unicode
from StringIO import StringIO
from tzlocal import get_localzone
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.intid.interfaces import IIntIds
from ZPublisher.Iterators import filestream_iterator
import json
import os
import uuid


ZIP_JOBS_KEY = 'opengever.meeting.zipexporter'
ZIP_EXPIRATION_DAYS = 2


def get_document_filename_for_zip(document, agenda_item_number):
    return normalize_path(u'{}/{}'.format(
        translate(
            _(u'title_agenda_item', default=u'Agenda item ${agenda_item_number}',
              mapping={u'number': agenda_item_number}),
            context=getRequest(),
            ),
        safe_unicode(document.get_filename()))
    )


def format_modified(modified):
    return safe_unicode(
        get_localzone().localize(
            modified.asdatetime().replace(tzinfo=None)
        ).isoformat())


class MeetingDocumentZipper(MeetingTraverser):

    def __init__(self, meeting, generator):
        super(MeetingDocumentZipper, self).__init__(meeting)
        self.generator = generator

    def get_zip_file(self):
        self.traverse()
        self.generator.add_file('meeting.json', self.get_meeting_json_file())
        return self.generator.generate()

    def traverse_protocol_document(self, document):
        self.generator.add_file(
            document.get_filename(), document.get_file().open()
        )

    def traverse_agenda_item_list_document(self, document):
        self.generator.add_file(
            document.get_filename(), document.get_file().open()
        )

    def traverse_agenda_item_document(self, document, agenda_item):
        self.generator.add_file(
            get_document_filename_for_zip(document, agenda_item.number),
            document.get_file().open()
        )

    def traverse_agenda_item_attachment(self, document, agenda_item):
        self.generator.add_file(
            get_document_filename_for_zip(document, agenda_item.number),
            document.get_file().open()
        )

    def get_meeting_json_file(self):
        return StringIO(MeetingJSONSerializer(self.meeting).get_json())


class MeetingJSONSerializer(MeetingTraverser):
    """Represents a JSON file with which grimlock can import the meeting."""

    def __init__(self, meeting):
        super(MeetingJSONSerializer, self).__init__(meeting)
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
            'file': document.get_filename(),
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
        self.current_agenda_item_data['number'] = agenda_item.number
        self.current_agenda_item_data['proposal'] = {
            'checksum': IBumblebeeDocument(document).get_checksum(),
            'file': get_document_filename_for_zip(document, agenda_item.number),
            'modified': format_modified(document.modified()),
        }

    def traverse_agenda_item_attachment(self, document, agenda_item):
        attachment_data = self.current_agenda_item_data.setdefault(
            'attachments', [])

        attachment_data.append({
            'checksum': IBumblebeeDocument(document).get_checksum(),
            'file': get_document_filename_for_zip(document, agenda_item.number),
            'modified': format_modified(document.modified()),
            'title': safe_unicode(document.Title()),
        })


class ZipExportDocumentCollector(MeetingTraverser):
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

    def traverse_agenda_item_attachment(self, document, agenda_item):
        self._collect(document)

    def get_documents(self):
        self.traverse()
        return tuple(self._documents)

    def _collect(self, document):
        if not IBumblebeeDocument(document).has_file_data():
            return

        self._documents.append(document)


class MeetingZipExporter(object):
    """Exports a meeting's documents in a zip file.

    Requests pdfs from bumblebee, if available. Falls back to original file
    if no pdf can be supplied or pdf conversion was skipped/erroneous.
    """

    def __init__(self, meeting, opaque_id=None, public_id=None):
        self.meeting = meeting
        self.committee = meeting.committee.oguid.resolve_object()

        # prepare annotations of committee
        annotations = IAnnotations(self.committee)
        if ZIP_JOBS_KEY not in annotations:
            annotations[ZIP_JOBS_KEY] = OOBTree()
        self.zip_jobs = annotations[ZIP_JOBS_KEY]

        # prepare or figure out public/internal ids
        if opaque_id and opaque_id in self.zip_jobs:
            self.internal_id = opaque_id
            self.zip_job = self.zip_jobs[self.internal_id]
            self.public_id = self.zip_job['public_id']
        elif public_id and public_id in self.zip_jobs:
            self.public_id = public_id
            self.zip_job = self.zip_jobs[self.public_id]
            self.internal_id = self.zip_job['internal_id']
        else:
            self.internal_id = opaque_id or uuid.uuid4()
            self.public_id = public_id or uuid.uuid4()
            self.zip_job = None

    def demand_pdfs(self):
        """Demand pdfs for all zip documents from bumlebee."""

        self._cleanup_old_jobs()

        self.zip_job = self._prepare_zip_job_metadata()
        documents = self._collect_meeting_documents()

        for folder, document in documents:
            status = self._queue_demand_job(document)
            self._append_document_job_metadata(
                self.zip_job, document, folder, status)

        return self.public_id

    def get_document(self, checksum):
        document_job = self.zip_job['documents'][checksum]
        return getUtility(IIntIds).getObject(document_job['intid'])

    def receive_pdf(self, checksum, mimetype, data):
        document_job = self.zip_job['documents'][checksum]
        filename = u'{}.pdf'.format(document_job['title'])
        blob_file = NamedBlobFile(
            data=data, contentType=mimetype, filename=filename)

        document_job['status'] = 'finished'
        document_job['blob'] = blob_file

    def mark_as_skipped(self, checksum):
        document_job = self.zip_job['documents'][checksum]
        document_job['status'] = 'skipped'

    def get_status(self):
        status = {
            'skipped': 0,
            'finished': 0,
            'converting': 0,
        }
        for document_info in self.zip_job['documents'].values():
            status[document_info['status']] += 1
        return status

    def zip_documents(self, generator):
        for document_info in self.zip_job['documents'].values():
            if document_info['status'] == 'finished':
                blob = document_info['blob']
                generator.add_file(blob.filename, blob.open())

    def _cleanup_old_jobs(self):
        """Remove expired zip jobs.

        The zip jobs are only kept for a relatively short amount of time as
        they are a temporary thing.
        """
        to_remove = set()
        now = utcnow_tz_aware()
        expiration_delta = timedelta(days=ZIP_EXPIRATION_DAYS)

        for zip_job in self.zip_jobs.values():
            delta = now - zip_job['timestamp']
            if delta > expiration_delta:
                to_remove.add(zip_job['public_id'])
                to_remove.add(zip_job['internal_id'])

        for id_ in to_remove:
            del self.zip_jobs[id_]

    def _prepare_zip_job_metadata(self):
        zip_job = OOBTree()
        zip_job['internal_id'] = self.internal_id
        zip_job['public_id'] = self.public_id
        zip_job['timestamp'] = utcnow_tz_aware()
        zip_job['documents'] = OOBTree()
        self.zip_jobs[self.internal_id] = zip_job
        self.zip_jobs[self.public_id] = zip_job

        return zip_job

    def _append_document_job_metadata(self, zip_job, document, folder, status):
        document_info = OOBTree()
        document_info['intid'] = getUtility(IIntIds).getId(document)
        document_info['title'] = safe_unicode(document.Title())
        document_info['folder'] = folder
        document_info['status'] = status

        checksum = IBumblebeeDocument(document).get_checksum()
        zip_job['documents'][checksum] = document_info

        return document_info

    def _queue_demand_job(self, document):
        callback_url = self.meeting.get_url(view='receive_meeting_zip_pdf')

        if get_service_v3().queue_demand(
                document, PROCESSING_QUEUE, callback_url,
                opaque_id=str(self.internal_id)):
            return 'converting'
        else:
            return 'skipped'

    def _collect_meeting_documents(self):
        return ZipExportDocumentCollector(self.meeting).get_documents()
