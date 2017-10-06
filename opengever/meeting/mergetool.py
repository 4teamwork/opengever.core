from docx import Document
from docxcompose.composer import Composer
from path import Path
import tempfile


class DocxMergeTool(object):
    """The docx merge tool merges docx documents with the docxcompose composer.

    It is used as a context manager and accepts GEVER documents (add_document)
    or Sablon instances (add_sablon).
    Calling the DocxMergeTool object merges the documents and returns the resulting
    bytes.
    The files are merged in the order they were added.
    """

    def __enter__(self):
        self._tempdir_path = Path(tempfile.mkdtemp(prefix='opengever.core.doxcmerge_'))
        self._file_paths = []
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._tempdir_path.rmtree_p()

    def add_document(self, document):
        """Add a opengever.document.document.
        """
        self._get_file().write_bytes(document.file.data)

    def add_sablon(self, sablon):
        """Add the document of a sablon instance, which is already processed.
        """
        self._get_file().write_bytes(sablon.file_data)

    def __call__(self):
        """Merge the registered docx files and return the resulting bytes.
        """
        if len(self._file_paths) == 0:
            raise ValueError('No files to merge.')

        composer = Composer(Document(self._file_paths[0]))
        map(composer.append, map(Document, self._file_paths[1:]))
        result_path = self._tempdir_path.joinpath('result.docx')
        composer.save(result_path)
        return result_path.bytes()

    def _get_file(self):
        path = self._tempdir_path.joinpath('{0}.docx'.format(len(self._file_paths)))
        self._file_paths.append(path)
        return path
