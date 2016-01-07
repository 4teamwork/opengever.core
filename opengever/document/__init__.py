from opengever.document.extra_mimetypes import register_additional_mimetypes
from opengever.document.officeconnector import register_ee_filename_callback
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('opengever.document')


# Register some additional well-known MIME types to help server-side file
# format recognition do a better job.
register_additional_mimetypes()

# Register a callback function for ZEM generation in Products.ExternalEditor
# to include a document's filename in the metadata.
register_ee_filename_callback()
