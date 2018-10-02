from BTrees.OOBTree import OOBTree
from ftw.bumblebee import get_service_v3
from ftw.bumblebee.config import PROCESSING_QUEUE
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.zipexport.utils import normalize_path
from opengever.base.date_time import utcnow_tz_aware
from opengever.meeting import _
from plone.namedfile.file import NamedBlobFile
from Products.CMFPlone.utils import safe_unicode
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.intid.interfaces import IIntIds
import uuid


ZIP_JOBS_KEY = 'opengever.meeting.zipexporter'


class MeetingZipExporter(object):
    """Exports a meeting's documents in a zip file.

    Requests pdfs from bumblebee, if available. Falls back to original file
    if no pdf can be supplied or pdf conversion was skipped/erroneous.
    """

    def __init__(self, meeting, committee, opaque_id=None, public_id=None):
        self.meeting = meeting
        self.committee = committee

        # prepare annotations of committee
        annotations = IAnnotations(self.committee)
        if ZIP_JOBS_KEY not in annotations:
            annotations[ZIP_JOBS_KEY] = OOBTree()
        self.zip_jobs = annotations[ZIP_JOBS_KEY]

        # prepare or figure out public/internal ids
        if opaque_id and opaque_id in self.zip_jobs:
            self.internal_id = opaque_id
            self.public_id = self.zip_jobs[self.internal_id]['public_id']
        elif public_id and public_id in self.zip_jobs:
            self.public_id = public_id
            self.internal_id = self.zip_jobs[self.public_id]['internal_id']
        else:
            self.internal_id = opaque_id or uuid.uuid4()
            self.public_id = public_id or uuid.uuid4()

    def demand_pdfs(self):
        """Demand pdfs for all zip documents from bumlebee."""

        zip_job = self._prepare_zip_job_metadata()
        documents = self._collect_meeting_documents()

        for folder, document in documents:
            status = self._queue_demand_job(document)
            self._append_document_job_metadata(
                zip_job, document, folder, status)

        return self.public_id

    def get_document(self, checksum):
        document_job = self.zip_jobs[self.internal_id]['documents'][checksum]
        return getUtility(IIntIds).getObject(document_job['intid'])

    def receive_pdf(self, checksum, mimetype, data):
        document_job = self.zip_jobs[self.internal_id]['documents'][checksum]
        filename = u'{}.pdf'.format(document_job['title'])
        blob_file = NamedBlobFile(
            data=data, contentType=mimetype, filename=filename)

        document_job['status'] = 'finished'
        document_job['blob'] = blob_file

    def mark_as_skipped(self, checksum):
        document_job = self.zip_jobs[self.internal_id]['documents'][checksum]
        document_job['status'] = 'skipped'

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
        documents = []
        if self.meeting.has_protocol_document():
            protocol = self.meeting.protocol_document.resolve_document()
            if protocol:
                documents.append((None, protocol))

        for agenda_item in self.meeting.agenda_items:
            folder_name = normalize_path(translate(
                _(u'title_agenda_item',
                  default=u'Agenda item ${number}',
                  mapping={u'number': agenda_item.number}),
                context=getRequest(),
            ))

            if agenda_item.has_submitted_documents():
                for document in agenda_item.proposal.resolve_submitted_documents():
                    documents.append((folder_name, document))

            if agenda_item.has_document:
                document = agenda_item.resolve_document()
                if document:
                    documents.append((folder_name, document))

        if self.meeting.has_agendaitem_list_document():
            agendaitem_list = self.meeting.agendaitem_list_document.resolve_document()
            if agendaitem_list:
                documents.append((None, agendaitem_list))

        # filter documents without file, they might have made their way in as
        # an attachment or somesuch
        return [(path, doc) for path, doc in documents
                if IBumblebeeDocument(doc).has_file_data()]
