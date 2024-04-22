from ftw.mail.attachment import AttachmentView as FtwAtachmentView
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from zExceptions import Forbidden


class AttachmentView(FtwAtachmentView):
    """Returns the attachment at the position specified in the request.
    """
    def render(self):
        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()
        return super(AttachmentView, self).render()

    def set_content_type(self, content_type, filename):
        if content_type == 'application/octet-stream':
            mtr = api.portal.get_tool('mimetypes_registry')
            content_type = mtr.globFilename(filename)
        super(AttachmentView, self).set_content_type(content_type, filename)

    def set_content_disposition(self, content_type, filename):
        set_attachment_content_disposition(self.request, filename)
