from ftw.bumblebee.browser.callback import BaseDemandCallbackView
from opengever.meeting.zipexport import MeetingZipExporter
from zExceptions import MethodNotAllowed
import uuid


class ReceiveZipPdf(BaseDemandCallbackView):

    def __call__(self):
        if self.request.method != 'POST':
            raise MethodNotAllowed()

        self.model = self.context.model
        self.committee = self.model.committee.oguid.resolve_object()

        return super(ReceiveZipPdf, self).__call__()

    def disable_csrf(self):
        """Do not disable csrf for this POST request."""
        return False

    def handle_success(self, mimetype, file_upload):
        self.get_exporter().receive_pdf(
            self.get_checksum(), mimetype, file_upload)

    def handle_error(self):
        self.get_exporter().mark_as_skipped(self.get_checksum())

    def handle_skipped(self):
        self.get_exporter().mark_as_skipped(self.get_checksum())

    def get_document(self):
        if not hasattr(self, '_document'):
            self._document = self.get_exporter().get_document(
                self.get_checksum())
        return self._document

    def get_exporter(self):
        if not hasattr(self, '_exporter'):
            self._exporter = MeetingZipExporter(
                self.model, opaque_id=self.get_opaque_id())
        return self._exporter

    def get_opaque_id(self):
        return uuid.UUID(super(ReceiveZipPdf, self).get_opaque_id())
