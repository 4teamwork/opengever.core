from opengever.document.extra_mimetypes import register_additional_mimetypes
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.document')


# Register some additional well-known MIME types to help server-side file
# format recognition do a better job.
register_additional_mimetypes()
