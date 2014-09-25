from five import grok
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.viewlets.download import DownloadFileVersion
from opengever.core import dictstorage
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.events import FileCopyDownloadedEvent
from plone import api
from plone.memoize import ram
from plone.memoize.interfaces import ICacheChooser
from plone.namedfile.browser import Download
from plone.namedfile.utils import stream_data
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from zope.component import queryUtility
from zope.event import notify
from zope.globalrequest import getRequest
from zope.i18n import translate


class DocumentishDownload(Download):
    """Overriding the Namefile Download view and implement some OpenGever
    specific file handling:

    - Deal with an unicode bug in plone.namedfile.utils.set_header
    - Set Content-Disposition headers based on browser sniffing
    - Fire our own `FileCopyDownloadedEvent`
    """

    def __call__(self):
        DownloadConfirmationHelper().process_request_form()

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

    def __init__(self):
        self.request = getRequest()

    def get_key(self, user=None):
        """ User specific key """
        user = user or api.user.get_current()
        return "download-confirmation-active-%s" % user.getId()

    @ram.cache(download_confirmation_user_cache_key)
    def is_active(self):
        """ Checks if the user has disabled download confirmation
        """
        key = self.get_key()
        return dictstorage.get(key) != 'False'

    def invalidate_is_active(self):
        chooser = queryUtility(ICacheChooser)
        key = 'opengever.document.browser.download.is_active'
        cache = chooser(key)
        cache.ramcache.invalidate(key)

    def deactivate(self):
        key = self.get_key()
        dictstorage.set(key, str(False))
        self.invalidate_is_active()

    def activate(self):
        key = self.get_key()
        dictstorage.set(key, str(True))
        self.invalidate_is_active()

    def get_html_tag(self, file_url, additional_classes=[], url_extension=''):
        if self.is_active():
            clazz = 'link-overlay {0}'.format(' '.join(additional_classes))
            url = '{0}/file_download_confirmation{1}'.format(
                file_url, url_extension)
        else:
            clazz = ' '.join(additional_classes)
            url = '{0}/download{1}'.format(file_url, url_extension)
        label = translate(_(u'label_download_copy',
                          default='Download copy'),
                          context=self.request).encode('utf-8')
        return '<a href="{0}" class="{1}">{2}</a>'.format(url, clazz, label)

    def process_request_form(self):
        """Process a request containing the rendered form."""

        if 'disable_download_confirmation' in self.request.form:
            DownloadConfirmationHelper().deactivate()


class DocumentDownloadFileVersion(DownloadFileVersion):
    """The default GEVER download file version view,
    but includes notifying FileCopyDownloadedEvent used for journalizing.
    """

    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.name('download_file_version')

    def render(self):
        DownloadConfirmationHelper().process_request_form()

        self._init_version_file()
        if self.version_file:
            notify(FileCopyDownloadedEvent(self.context))
        return super(DocumentDownloadFileVersion, self).render()
