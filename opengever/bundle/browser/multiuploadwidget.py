from z3c.form import widget
from z3c.form.browser.file import FileWidget
from z3c.form.converter import FileUploadDataConverter
from z3c.form.i18n import MessageFactory as zf_mf
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFileWidget
from z3c.form.interfaces import IFormLayer
from zope import schema
from zope.component import adapter
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ITuple
from ZPublisher.HTTPRequest import FileUpload


class IMultiFileUploadWidget(IFileWidget):
    pass


class IMultiFileUploadField(ITuple):
    pass


@implementer(IMultiFileUploadField, IFromUnicode)
class MultiFileUploadField(schema.Tuple):

    def validate(self, value):
        if not value and self.required:
            raise RequiredMissing(self.__name__)


@implementer_only(IMultiFileUploadWidget)
class MultiFileUploadWidget(FileWidget):

    accept = '.json'

    def json_data(self):
        raise NotImplementedError


class MultiFileUploadDataConverter(FileUploadDataConverter):

    adapts(
        IMultiFileUploadField, IMultiFileUploadWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""

        if isinstance(value, list):
            return tuple([self.convert_upload(upload) for upload in value])
        return ()

    def convert_upload(self, upload):
        if not isinstance(upload, FileUpload):
            return None

        headers = upload.headers
        filename = upload.filename
        try:
            seek = upload.seek
            read = upload.read
        except AttributeError as e:
            raise ValueError(zf_mf('Bytes data are not a file object'), e)
        else:
            seek(0)
            data = read()
            if data or getattr(upload, 'filename', ''):
                return {
                    'filename': filename,
                    'headers': headers,
                    'data': data,
                }
            else:
                return self.field.missing_value


@adapter(IMultiFileUploadField, IFormLayer)
@implementer(IFieldWidget)
def MultiFileUploadFieldWidget(field, request):
    return widget.FieldWidget(field, MultiFileUploadWidget(request))
