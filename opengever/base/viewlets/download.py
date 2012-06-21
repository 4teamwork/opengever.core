from five import grok
from opengever.base import _
from opengever.base.behaviors.utils import PrimaryFieldInfo
from opengever.base.behaviors.utils import set_attachment_content_disposition
from plone.app.versioningbehavior.behaviors import IVersioningSupport
from Products.statusmessages.interfaces import IStatusMessage


class DownloadFileVersion(grok.View):
    grok.context(IVersioningSupport)
    grok.require('zope2.View')
    grok.name('download_file_version')

    def render(self):
        version_id = self.request.get('version_id')
        pr = self.context.portal_repository
        old_obj = pr.retrieve(self.context, version_id).object
        primary_field_info = PrimaryFieldInfo(old_obj)
        old_file = primary_field_info.value
        if not old_file:
            msg = _(u'No file in in this version')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader('Content-Type', old_file.contentType)
        response.setHeader('Content-Length', old_file.getSize())
        set_attachment_content_disposition(
            self.request, old_file.filename.encode('utf-8'))

        return old_file.data
