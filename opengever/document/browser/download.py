from opengever.api.utils import raise_for_api_request
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.viewlets.download import DownloadFileVersion
from opengever.core import dictstorage
from opengever.document import _
from opengever.document.browser.edit import get_redirect_url
from opengever.document.events import FileCopyDownloadedEvent
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.mail.mail import IOGMailMarker
from opengever.virusscan.validator import validateDownloadIfNecessary
from opengever.workspace.utils import is_restricted_workspace_and_guest
from plone import api
from plone.dexterity.utils import safe_utf8
from plone.memoize import ram
from plone.memoize.interfaces import ICacheChooser
from plone.namedfile.browser import Download
from plone.namedfile.utils import stream_data
from plone.protect.utils import addTokenToUrl
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zExceptions import Forbidden
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import Invalid
from zope.publisher.interfaces import NotFound


class DocumentishDownload(Download):
    """Overriding the Namefile Download view and implement some OpenGever
    specific file handling:

    - Deal with an unicode bug in plone.namedfile.utils.set_header
    - Set Content-Disposition headers based on browser sniffing
    - Fire our own `FileCopyDownloadedEvent`
    - Redirect with notification when instead of raising 404 for missing files
    - Download the latest version instead the current working copy if the
      document is checked out by another user
    - Scan for viruses if enabled in IAVScannerSettings
    """

    def __call__(self):
        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()

        if self.is_checked_out_by_another_user():
            current_version_id = self.context.get_current_version_id()
            if current_version_id is not None:
                self.request['version_id'] = current_version_id
            return DocumentDownloadFileVersion(self.context, self.request)()

        DownloadConfirmationHelper(self.context).process_request_form()

        try:
            named_file = self._getFile()
        except NotFound:
            msg = _(
                u'The Document ${title} has no File.',
                mapping={'title': self.context.Title().decode('utf-8')})
            api.portal.show_message(msg, self.request, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))

        self.extract_filename(named_file)
        try:
            validateDownloadIfNecessary(self.filename, named_file, self.request)
        except Invalid as exc:
            raise_for_api_request(self.request, BadRequest(exc.message))
            api.portal.show_message(exc.message, self.request, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context))

        set_attachment_content_disposition(self.request, self.filename,
                                           named_file)
        notify(FileCopyDownloadedEvent(self.context))

        return self.stream_data(named_file)

    def extract_filename(self, named_file):
        if not self.filename:
            self.filename = getattr(named_file, 'filename', self.fieldname)

        if self.filename:
            self.filename = safe_utf8(self.filename)

    def stream_data(self, named_file):
        return stream_data(named_file)

    def is_checked_out_by_another_user(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        return manager and manager.is_checked_out_by_another_user()


class DownloadConfirmation(BrowserView):
    """Download Confirmation View, allways displayed in a overlay."""

    template = ViewPageTemplateFile('templates/downloadconfirmation.pt')

    def __call__(self):
        return self.template()

    def download_url(self):
        if self.request.get('version_id'):
            return '%s/download_file_version?version_id=%s&error_as_message=1' % (
                self.context.absolute_url(),
                self.request.get('version_id'))
        else:
            return '%s/download?error_as_message=1' % (self.context.absolute_url())

    def download_available(self):
        """ check whether download is available.
        """
        return self.context.file is not None

    def msg_no_file_available(self):
        return _(u'The Document ${title} has no File.',
                 mapping={'title': self.context.Title().decode('utf-8')})


def download_confirmation_user_cache_key(func, ctx):
    userid = getToolByName(
        getSite(), 'portal_membership').getAuthenticatedMember().getId()
    return "%s-" % (userid)


class DownloadConfirmationHelper(object):
    """Tracks per user state of download confirmations."""

    def __init__(self, context):
        self.request = getRequest()
        self.context = context

    def get_key(self, user=None):
        """User specific key."""
        user = user or api.user.get_current()
        return "download-confirmation-active-%s" % user.getId()

    @ram.cache(download_confirmation_user_cache_key)
    def is_active(self):
        """Checks if the user has disabled download confirmation."""
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

    def get_html_tag(self, additional_classes=[], url_extension='',
                     viewname='download', include_token=False):
        file_url = self.context.absolute_url()

        # Do not display a download confirmation for mail items
        if self.is_active() and not IOGMailMarker.providedBy(self.context):
            viewname = 'file_download_confirmation'
            clazz = (('link-overlay '
                      'modal '
                      '{0}')
                     .format(' '.join(additional_classes)))
        else:
            clazz = ' '.join(additional_classes)

        if url_extension:
            url_extension += "&error_as_message=1"
        else:
            url_extension += "?error_as_message=1"
        url = '{0}/{1}{2}'.format(file_url, viewname, url_extension)
        if include_token:
            url = addTokenToUrl(url)

        label = translate(_(u'label_download_copy', default='Download copy'),
                          context=self.request).encode('utf-8')

        return ('<a href="{0}" '
                'id="action-download" '
                'class="{1}">{2}</a>').format(url, clazz, label)

    def process_request_form(self):
        """Process a request containing the rendered form."""
        if 'disable_download_confirmation' in self.request.form:
            DownloadConfirmationHelper(self.context).deactivate()


class DocumentDownloadFileVersion(DownloadFileVersion):
    """The default GEVER download file version view,
    but includes notifying FileCopyDownloadedEvent used for journalizing.
    """

    def __call__(self):
        if is_restricted_workspace_and_guest(self.context):
            raise Forbidden()

        DownloadConfirmationHelper(self.context).process_request_form()

        self._init_version_file()
        if self.version_file:
            try:
                validateDownloadIfNecessary(
                    self.version_file.filename.encode('utf-8'),
                    self.version_file,
                    self.request)
            except Invalid as exc:
                raise_for_api_request(self.request, BadRequest(exc.message))
                api.portal.show_message(exc.message, self.request, type='error')
                return self.request.RESPONSE.redirect(
                    get_redirect_url(self.context))

            notify(FileCopyDownloadedEvent(
                self.context,
                getattr(self.request, 'version_id', None)))
        return super(DocumentDownloadFileVersion, self).render()
