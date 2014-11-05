from opengever.document.browser.download import DocumentishDownload
from plone.namedfile.interfaces import HAVE_BLOBS

if HAVE_BLOBS:
    from plone.namedfile.interfaces import IBlobby


class MailDownload(DocumentishDownload):
    """Because MS Outlook has problems displaying *.eml mails
    with lf line endings, we make sure that we only deliver CRLF.

    To do that conversion manually we can't use an filestream_iterator,
    for streaming the data.
    """

    def convert_line_endings(self, filename):
        lines = []
        with open(filename, 'r') as _file:
            for line in _file:
                if not line.endswith('\r\n'):
                    line = '{}\r\n'.format(line[:-1])
                    lines.append(line)

        return ''.join(lines)

    def stream_data(self, named_file):
        if HAVE_BLOBS:
            if IBlobby.providedBy(named_file):
                if named_file._blob._p_blob_uncommitted:
                    filename = named_file._blob._p_blob_uncommitted
                else:
                    filename = named_file._blob.committed()

                return self.convert_line_endings(filename)

        return named_file.data
