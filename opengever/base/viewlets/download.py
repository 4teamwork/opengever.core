from five import grok
from opengever.base import _
from opengever.base.behaviors.utils import PrimaryFieldInfo
from opengever.base.behaviors.utils import set_attachment_content_disposition
from plone.app.versioningbehavior.behaviors import IVersioningSupport
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage


class DownloadFileVersion(grok.View):
    grok.context(IVersioningSupport)
    grok.require('zope2.View')
    grok.name('download_file_version')

    def _init_version_file(self):
        version_id = self.request.get('version_id')
        pr = getToolByName(self.context, 'portal_repository')
        old_obj = pr.retrieve(self.context, version_id).object
        primary_field_info = PrimaryFieldInfo(old_obj)
        self.version_file = primary_field_info.value

    def render(self):

        self._init_version_file()
        if not self.version_file:
            msg = _(u'No file in in this version')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader('Content-Type', self.version_file.contentType)
        response.setHeader('Content-Length', self.version_file.getSize())
        set_attachment_content_disposition(
            self.request, self.version_file.filename.encode('utf-8'))

        return self.version_file.data
