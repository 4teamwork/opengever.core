from ftw.mail.mail import IMail
from opengever.document.browser.download import DocumentishDownload
from opengever.mail.interfaces import IMailDownloadSettings
from opengever.mail.mail import IOGMail
from os.path import splitext
from plone.namedfile.interfaces import HAVE_BLOBS
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


if HAVE_BLOBS:
    from plone.namedfile.interfaces import IBlobby


def p7m_extension_replacement():
    """Get the client specific extension that should be used to replace p7m
    extension in Mail downloads."""
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IMailDownloadSettings)
    return proxy.p7m_extension_replacement


class MailDownload(DocumentishDownload):
    """
    We overwrite the document download for mails for two outlook issues:

    1. MS Outlook has problems displaying *.eml mails with lf line endings,
    so we make sure that we only deliver CRLF. To do that conversion manually
    we can't use an filestream_iterator, for streaming the data.

    2. MS Outlook refuses to open .p7m files so we change the extension to .eml
    for the download.
    """

    def publishTraverse(self, request, name):
        """Do not raise NotFound error if fieldname and filename is not
        specified.
        """

        if self.fieldname is None:  # ../@@download/fieldname
            self.fieldname = name
        elif self.filename is None:  # ../@@download/fieldname/filename
            self.filename = name

        return self

    def convert_line_endings(self, filename):
        lines = []
        with open(filename, 'r') as _file:
            for line in _file:
                if not line.endswith('\r\n'):
                    line = '{}\r\n'.format(line[:-1])

                lines.append(line)

        return ''.join(lines)

    def _getFile(self):
        if not self.fieldname:
            if self.context.original_message:
                self.fieldname = IOGMail['original_message'].getName()
            else:
                self.fieldname = IMail['message'].getName()

        return super(MailDownload, self)._getFile()

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
            self.filename = '.'.join((root, p7m_extension_replacement()))
