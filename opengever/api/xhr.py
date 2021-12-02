from ftw.mail.mail import IMail
from opengever.api.add import GeverFolderPost
from opengever.document.document import IDocumentSchema
from opengever.document.document import is_email_upload
from zExceptions import BadRequest


class XHRUploadPost(GeverFolderPost):
    """XHR document upload endpoint with multipart/form-data
    """

    @property
    def request_data(self):
        form_data = self.request.form
        title = form_data.get('title', '').decode('utf-8')
        request_data = {
            '@type': 'ftw.mail.mail' if is_email_upload(self.filename) else 'opengever.document.document'
            }

        if title:
            request_data['title'] = title

        return request_data

    def extract_data(self):
        self.file_upload = self.request.form.get('file')

        if not self.file_upload:
            raise BadRequest('Property "file" is required')

        self.filename = self.file_upload.filename.decode('utf-8')
        self.content_type = self.file_upload.headers.get('Content-Type')

        return super(XHRUploadPost, self).extract_data()

    def before_deserialization(self, obj):
        field = IDocumentSchema['file']
        if obj.is_mail:
            field = IMail['message']

        namedblobfile = field._type(
            data=self.file_upload,
            contentType=self.content_type,
            filename=self.filename)

        field.set(field.interface(obj), namedblobfile)
