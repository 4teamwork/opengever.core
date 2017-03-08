from ftw.upgrade import UpgradeStep
from ftw.upgrade.progresslogger import ProgressLogger
from plone.namedfile.interfaces import INamedBlobFile
from plone.namedfile.utils import get_contenttype


class SetCorrectMessageContentTypeForDragDropUploadedMails(UpgradeStep):
    """Set correct message contentType for drag&drop uploaded mails.

    When drag&drop uploading *.msg files the filename was temporarily incorrect
    in some cases. This lead to the mimetype being guessed as
    application/octet-stream instead of the expected message/rfc822 for *.eml
    files.

    This leads to issues with bumblebee which does not convert mails that have
    a mime type of application/octet-stream.

    This upgrade step checks the mails and has a look at all of them that
    are not of the expected mime-type. It then sets the mime-type to what would
    be set by `get_contenttype` while creating their `NamedBlobFile`.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'portal_type': 'ftw.mail.mail'}
        msg = 'Set correct message contentType for mails.'

        for brain in ProgressLogger(
                msg, self.catalog_unrestricted_search(query)):
            self.ensure_correct_content_type(brain)

    def ensure_correct_content_type(self, brain):
        """Make sure that the contentType of a mail's message is what would
        be returned by `get_contenttype`.
        """

        if self.has_expected_content_type(brain):
            return

        mail = brain.getObject()
        message = getattr(mail, 'message', None)
        if not message:
            return

        # can't be paranoid enough sometimes ...
        if not INamedBlobFile.providedBy(message):
            return

        if not getattr(message, 'filename', None):
            return

        content_type = get_contenttype(filename=message.filename)
        if not content_type:
            return

        message.contentType = content_type
        # we're actually interested in updating metadata only, but since we
        # can't just chose a cheap index to achieve that.
        mail.reindexObject(idxs=['id'])

    def has_expected_content_type(self, brain):
        return brain.getContentType == 'message/rfc822'
