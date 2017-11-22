from docx import Document
from docxcompose.composer import Composer
from docxcompose.properties import CustomProperties
from path import Path
import tempfile


class DocxMergeTool(object):
    """The docx merge tool merges docx documents with the docxcompose composer.
    The merge is based on a master document, if remove_property_fields is False
    the master's doc-properties will be preserved.

    It is used as a context manager and accepts bytes of documents.
    Calling the DocxMergeTool object merges the documents and returns the resulting
    bytes.

    The files are merged in the order they were added or inserted as as
    specified by inserts index.
    """

    def __init__(self, master, remove_property_fields=True):
        self._remove_property_fields = remove_property_fields
        self._master = master

    def __enter__(self):
        self._tempdir_path = Path(tempfile.mkdtemp(prefix='opengever.core.doxcmerge_'))
        self._index = 0
        self._composer = Composer(self._as_document(self._master))

        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._tempdir_path.rmtree_p()

    def __call__(self):
        """Merge the registered docx files and return the resulting bytes.
        """
        result_path = self._tempdir_path.joinpath('result.docx')
        self._composer.save(result_path)
        return result_path.bytes()

    def add(self, file_data):
        self._composer.append(
            self._as_document(file_data),
            remove_property_fields=self._remove_property_fields)

    def insert(self, index, file_data):
        self._composer.insert(
            index, self._as_document(file_data),
            remove_property_fields=self._remove_property_fields)

    def _as_document(self, file_data):
        """Convert bytes to a document.

        Also make sure property field value are up to date before they are
        removed.
        """
        path = self._get_next_path()
        path.write_bytes(file_data)
        document = Document(path)

        if self._remove_property_fields:
            CustomProperties(document).update_all()

        return document

    def _get_next_path(self):
        path = self._tempdir_path.joinpath('{0}.docx'.format(self._index))
        self._index += 1
        return path
