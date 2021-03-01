from datetime import datetime
from persistent.dict import PersistentDict
from plone.formwidget.namedfile.interfaces import IFileUploadTemporaryStorage
from plone.formwidget.namedfile.widget import NamedFileWidget
from plone.namedfile.interfaces import INamed
from zope.component.hooks import getSite
import uuid


class GeverNamedFileWidget(NamedFileWidget):

    @property
    def file_upload_id(self):
        """Temporary store the uploaded file contents with a file_upload_id key.
        In case of form validation errors the already uploaded image can then
        be reused.
        """
        if self._file_upload_id:
            # cache this property for multiple calls within one request.
            # This avoids storing a file upload multiple times.
            return self._file_upload_id

        upload_id = None
        if self.is_uploaded:
            data = None
            if INamed.providedBy(self.value):
                # data = self.value.data
                # Here we diverge, otherwise we would create a new
                # copy of the file in the storage for each time we
                # access the edit form
                return None
                # previously uploaded and failed

            else:
                self.value.seek(0)
                data = self.value.read()

            upload_id = uuid.uuid4().hex
            up = IFileUploadTemporaryStorage(getSite())
            up.cleanup()
            up.upload_map[upload_id] = PersistentDict(
                filename=self.value.filename,
                data=data,
                dt=datetime.now(),
            )

        self._file_upload_id = upload_id
        return upload_id
