from Products.CMFCore.utils import getToolByName
from five import grok
from ftw.dictstorage.interfaces import IDictStorage
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.dictstorage import DictStorageConfigurationContext
from opengever.base.viewlets.download import DownloadFileVersion
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.events import FileCopyDownloadedEvent
from plone.memoize import ram
from plone.memoize.ram import global_cache
from plone.namedfile.browser import Download
from plone.namedfile.utils import stream_data
from zope.app.component.hooks import getSite
from zope.event import notify
from zope.i18n import translate
from zope.component import queryUtility
from plone.memoize.interfaces import ICacheChooser


class DocumentishDownload(Download):
    """Overriding the Namefile Download view and implement some OpenGever
    specific file handling:

    - Deal with an unicode bug in plone.namedfile.utils.set_header
    - Set Content-Disposition headers based on browser sniffing
    - Fire our own `FileCopyDownloadedEvent`
    """

    def __call__(self):
        if 'disable_download_confirmation' in self.request.form:
            dc_helper = DownloadConfirmationHelper(self.context, self.request)
            dc_helper.deactivate()

        named_file = self._getFile()
        if not self.filename:
            self.filename = getattr(named_file, 'filename', self.fieldname)

        if self.filename:
            self.filename = self.filename.encode('utf-8')

        set_attachment_content_disposition(self.request, self.filename,
                                           named_file)
        notify(FileCopyDownloadedEvent(self.context))
        return stream_data(named_file)


class DownloadConfirmation(grok.View):
    """Download Confirmation View, allways displayed in a overlay.
    """

    grok.context(IDocumentSchema)
    grok.name('file_download_confirmation')
    grok.require('zope2.View')

    def download_url(self):
        if self.request.get('version_id'):
            return '%s/download_file_version?version_id=%s' % (
                self.context.absolute_url(),
                self.request.get('version_id'))
        else:
            return '%s/download' % (self.context.absolute_url())

    def download_available(self):
        return self.context.file is not None

    def msg_no_file_available(self):
        return _(u'The Document ${title} has no File',
                 mapping={'title': self.context.Title().decode('utf-8')})


def download_confirmation_user_cache_key(func, ctx):
    userid = getToolByName(
        getSite(), 'portal_membership').getAuthenticatedMember().getId()
    return "%s-" % (userid)


class DownloadConfirmationHelper(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_key(self):
        """ User specific key """
        userid = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember().getId()
        return "download-confirmation-active-%s" % userid

    @ram.cache(download_confirmation_user_cache_key)
    def is_active(self):
        """ Checks if the user has disabled download confirmation
        """
        storage = IDictStorage(DictStorageConfigurationContext())
        key = self.get_key()
        return storage.get(key) != "disabled"

    def invalidate_is_active(self):
        chooser = queryUtility(ICacheChooser)
        key = 'opengever.document.browser.download.is_active'
        cache = chooser(key)
        cache.ramcache.invalidate(key)

    def deactivate(self):
        storage = IDictStorage(DictStorageConfigurationContext())
        key = self.get_key()
        storage.set(key, "disabled")
        self.invalidate_is_active()

    def activate(self):
        storage = IDictStorage(DictStorageConfigurationContext())
        key = self.get_key()
        storage.set(key, None)
        self.invalidate_is_active()

    def get_html_tag(self, file_url, additional_classes=[], url_extension=''):
        data = {}
        if self.is_active():
            data['class'] = 'link-overlay %s' % ' '.join(additional_classes)
            data['url'] = '%s/file_download_confirmation%s' % (file_url,
                                                               url_extension)
        else:
            data['class'] = ' '.join(additional_classes)
            data['url'] = '%s/download%s' % (file_url, url_extension)
        data['label'] = translate(_(u'label_download_copy'),
                                  context=self.request).encode('utf-8')
        return '<a href="%(url)s" class="%(class)s">%(label)s</a>' % data


class DocumentDownloadFileVersion(DownloadFileVersion):
    """The default GEVER download file version view,
    but includes notifying FileCopyDownloadedEvent used for journalizing.
    """

    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.name('download_file_version')

    def render(self):
        if 'disable_download_confirmation' in self.request.form:
            dc_helper = DownloadConfirmationHelper(self.context, self.request)
            dc_helper.deactivate()

        self._init_version_file()
        if self.version_file:
            notify(FileCopyDownloadedEvent(self.context))
        return super(DocumentDownloadFileVersion, self).render()
