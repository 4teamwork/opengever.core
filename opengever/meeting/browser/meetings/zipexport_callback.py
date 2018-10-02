from ftw.bumblebee.browser.callback import BaseConvertCallbackView
from ftw.bumblebee.hashing import get_derived_secret
from ftw.bumblebee.hashing import verify_one_time_token
from ftw.bumblebee.interfaces import IBumblebeeJournal
from opengever.meeting.zipexport import MeetingZipExporter
from plone.uuid.interfaces import IUUID
from zExceptions import MethodNotAllowed
import uuid


class ReceiveZipPdf(BaseConvertCallbackView):

    def __call__(self):
        if self.request.method != 'POST':
            raise MethodNotAllowed()

        self.model = self.context.model
        self.committee = self.model.committee.oguid.resolve_object()

        return super(ReceiveZipPdf, self).__call__()

    def disable_csrf(self):
        """Do not disable csrf for this POST request."""
        pass

    def handle_success(self, mimetype, file_upload):
        self.get_exporter().receive_pdf(
            self.get_checksum(), mimetype, file_upload)

    def journalize_success(self):
        return IBumblebeeJournal(self.get_document()).add(
            'Demand callback successful.')

    def handle_error(self):
        self.get_exporter().mark_as_skipped(self.get_checksum())

    def journalize_failure(self):
        return IBumblebeeJournal(self.get_document()).add(
            'Demand callback failed ({}).'.format(
                self.get_body().get('error')))

    def handle_skipped(self):
        self.get_exporter().mark_as_skipped(self.get_checksum())

    def journalize_skipped(self):
        return IBumblebeeJournal(self.get_document()).add(
            'Demand callback skipped ({}).'.format(
                self.get_body().get('error')))

    def verify_token(self):
        token = self.get_body().get('token')
        return token and verify_one_time_token(
            secret=get_derived_secret('one time token for download'),
            token=token,
            content=IUUID(self.get_document()))

    def get_body(self):
        return self.request

    def get_document(self):
        if not hasattr(self, '_document'):
            self._document = self.get_exporter().get_document(
                self.get_checksum())
        return self._document

    def get_exporter(self):
        if not hasattr(self, '_exporter'):
            self._exporter = MeetingZipExporter(
                self.model, self.committee, opaque_id=self.get_opaque_id())
        return self._exporter

    def get_file_data(self):
        """Return mimetype but don't read fileupload into memory yet."""

        file_upload = self.get_body().get('pdf')
        mimetype = file_upload.headers.get('content-type', None)
        return mimetype, file_upload

    def get_opaque_id(self):
        return uuid.UUID(self.get_body().get('opaque_id'))

    def get_checksum(self):
        return self.get_body().get('document')
