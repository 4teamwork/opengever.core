from ftw.mail import utils
from ftw.mail.attachment import AttachmentView as FtwAtachmentView
from ftw.mail.utils import walk
from opengever.base.behaviors.utils import set_attachment_content_disposition
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from ZODB.POSException import ConflictError
import email


class AttachmentView(FtwAtachmentView):
    """Returns the attachment at the position specified in the request.
    """

    def render(self):
        """ Copied from ftw.mail.attachment:
        Just add the contenttype-check (see l.51)
        """

        if self.message is None:
            raise NotFound
        message = email.message_from_string(self.message.data)

        # we need an int value for the position
        pos = 0
        try:
            pos = int(self.position)
        except ValueError:
            raise NotFound

        # get attachment at position pos
        attachment = None
        for i, part in enumerate(walk(message)):
            if i == pos:
                attachment = part
                continue

        if attachment is not None:
            content_type = attachment.get_content_type()
            filename = utils.get_filename(attachment)
            if filename is None:
                raise NotFound

            # the the konsul migrated mails, often has a wrong
            # content-type for word documents, therefore we check the
            # content-type, in this case we guess it over the filename
            if content_type == 'application/octet-stream':
                mtr = getToolByName(self.context, 'mimetypes_registry')
                content_type = mtr.globFilename(filename)

            # make sure we have a unicode string
            if not isinstance(filename, unicode):
                filename = filename.decode('utf-8', 'ignore')
            # internet explorer and safari don't like rfc encoding of filenames
            # and they don't like utf encoding too.
            # therefore we first try to encode the filename in iso-8859-1
            try:
                filename = filename.encode('iso-8859-1')
            except ConflictError:
                raise
            except Exception:
                filename = filename.encode('utf-8', 'ignore')

            self.request.response.setHeader('Content-Type', content_type)
            set_attachment_content_disposition(self.request, filename)

            if content_type == 'message/rfc822':
                return attachment.as_string()
            return attachment.get_payload(decode=1)

        raise NotFound
