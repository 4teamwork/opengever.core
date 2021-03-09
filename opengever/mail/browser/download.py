from opengever.document.browser.download import DocumentishDownload
from opengever.mail.mail import IOGMail
from os.path import splitext
from plone.namedfile.interfaces import HAVE_BLOBS

if HAVE_BLOBS:
    from plone.namedfile.interfaces import IBlobby


class MailDownload(DocumentishDownload):
    """
    We overwrite the document download for mails for two outlook issues:

    1. MS Outlook has problems displaying *.eml mails with lf line endings,
    so we make sure that we only deliver CRLF. To do that conversion manually
    we can't use an filestream_iterator, for streaming the data.

    2. MS Outlook refuses to open .p7m files so we change the extension to .eml
    for the download.
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
        if self.fieldname == IOGMail['original_message'].getName():
            return super(MailDownload, self).stream_data(named_file)

        if HAVE_BLOBS:
            if IBlobby.providedBy(named_file):
                if named_file._blob._p_blob_uncommitted:
                    filename = named_file._blob._p_blob_uncommitted
                else:
                    filename = named_file._blob.committed()

                return self.convert_line_endings(filename)

        return named_file.data

    def extract_filename(self, named_file):
        super(MailDownload, self).extract_filename(named_file)
        if not self.filename:
            return
        root, ext = splitext(self.filename)
        if ext == '.p7m':
            self.filename = '.'.join((root, 'eml'))
