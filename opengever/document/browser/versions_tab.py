from Acquisition import aq_parent
from datetime import datetime
from five import grok
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.base.protect import unprotected_write
from opengever.document import _
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.actor import Actor
from opengever.tabbedview.browser.base import BaseListingTab
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.CMFPlone.utils import safe_unicode
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface
import pkg_resources

try:
    pkg_resources.get_distribution('opengever.pdfconverter')
except pkg_resources.DistributionNotFound:
    PDFCONVERTER_AVAILABLE = False
else:
    PDFCONVERTER_AVAILABLE = True


def translate_link(url, label, css_class=None):
    """Create a formatted link with the link text translated into the current
    user's language, and optional CSS classes.
    """
    link_text = translate(
        label,
        domain='opengever.document', context=getRequest())

    klass = u''
    if css_class:
        klass = u'class="{}"'.format(safe_unicode(css_class))

    link = u'<a href="{}" {}>{}</a>'.format(
        safe_unicode(url), klass, link_text)
    return link


class VersionDataProxy(object):
    """A proxy for CMFEditions `VersionData` objects (representing a single
    version of a particular object).

    This proxy object provides easier attribute access to some of the
    VersionData's metadata, so we can use decent column names in the
    VersionsTab below.

    It also provides some helper methods for building data that ends up in
    the columns but isn't directly accessible.
    """

    def __init__(self, version_data, url):
        self._version_data = version_data
        self._url = url

    def __getattr__(self, name):
        return getattr(self._version_data, name)

    @property
    def url(self):
        """Absolute URL of the object that this version belongs to.
        """
        return self._url

    @property
    def version(self):
        """The ID ("number") of this version.
        """
        return self._version_data.version_id

    @property
    def actor(self):
        """Returns a formatted link to the actor that created this version.
        """
        principal = self._version_data.sys_metadata['principal']
        actor = Actor.user(principal)
        return actor.get_link()

    @property
    def timestamp(self):
        """Creation timestamp of this version, formatted as localized time.
        """
        ts = self._version_data.sys_metadata['timestamp']
        dt = datetime.fromtimestamp(ts)
        return api.portal.get_localized_time(datetime=dt, long_format=True)

    @property
    def comment(self):
        """Comment for this version.
        """
        return self._version_data.sys_metadata['comment']

    @property
    def download_link(self):
        """Returns a formatted link that allows to download a copy of this
        version (opens in an overlay).
        """
        dc_helper = DownloadConfirmationHelper()
        link = dc_helper.get_html_tag(
            self.url,
            url_extension="?version_id=%s" % self.version_id,
            additional_classes=['standalone', 'function-download-copy'],
            viewname='download_file_version',
            include_token=True)
        return link

    @property
    def pdf_preview_link(self):
        """Returns a formatted link to download the PDF preview for this
        version (only rendered if opengever.pdfconverter is available).
        """
        url = '{}/download_pdf_version?version_id={}'
        url = url.format(self.url, self.version_id)
        url = addTokenToUrl(url)
        link = translate_link(
            url, _(u'button_pdf', default=u'PDF'),
            css_class='standalone function-download-pdf')
        return link

    @property
    def revert_link(self):
        """Returns a formatted link to revert to this particular version.
        """
        url = '{}/revert-file-to-version?version_id={}'
        url = url.format(self.url, self.version_id)
        url = addTokenToUrl(url)
        link = translate_link(
            url, _(u'label_reset', default=u'reset'),
            css_class='standalone function-revert')
        return link


class LazyHistoryProxy(object):
    """A proxy for CMFEditions `LazyHistory` that preserves its lazy iteration
    properties, but returns `VersionDataProxy` objects instead.
    """

    def __init__(self, history, url):
        self._history = history
        self._url = url

    def __len__(self):
        return self._history.__len__()

    def __getitem__(self, idx):
        item = self._history.__getitem__(idx)
        return VersionDataProxy(item, self._url)

    def __iter__(self):
        return self._history.__iter__()


class IVersionsSourceConfig(ITableSourceConfig):
    """
    """


class VersionsTableSource(grok.MultiAdapter, BaseTableSource):
    """Table source that returns a wrapped LazyHistory for CMFEditions
    versions.
    """

    grok.implements(ITableSource)
    grok.adapts(IVersionsSourceConfig, Interface)

    def search_results(self, query):
        # `query` , as generated by `VersionsTab.get_base_query()`,  is
        # actually the object we're displaying the version history for
        obj = query

        # CMFEditions causes writes to the parent when retrieving versions
        unprotected_write(aq_parent(obj))

        repo_tool = api.portal.get_tool('portal_repository')
        history = repo_tool.getHistory(obj)
        return LazyHistoryProxy(history, obj.absolute_url())


class VersionsTab(BaseListingTab):
    """Implements a 'Versions' tab on documents.

    Displays the document's CMFEditions versions in a lazily batched fashion.
    """

    implements(IVersionsSourceConfig)

    grok.name('tabbedview_view-versions')
    grok.require('zope2.View')
    grok.context(IDocumentSchema)

    sort_on = 'version'
    sort_reverse = True

    show_selects = False
    enabled_actions = []
    major_actions = []

    batching_enabled = True
    lazy = True

    _columns = (
        {'column': 'version',
         'column_title': _(u'label_version', default=u'Version'),
         },

        {'column': 'actor',
         'column_title': _(u'label_actor', 'Changed by'),
         },

        {'column': 'timestamp',
         'column_title': _(u'label_date', default=u'Date'),
         },

        {'column': 'comment',
         'column_title': _(u'label_comment', default=u'Comment'),
         },

        {'column': 'download_link',
         'column_title': ' ',
         },

        # Dropped if PDFCONVERTER_AVAILABLE == False
        {'column': 'pdf_preview_link',
         'column_title': ' ',
         },

        {'column': 'revert_link',
         'column_title': ' ',
         },
    )

    @property
    def columns(self):
        """Disable pdf_preview link in deployments without pdfconverter.
        """
        if not PDFCONVERTER_AVAILABLE:
            return filter(
                lambda c: c['column'] != 'pdf_preview_link', self._columns)

        return self._columns

    def get_base_query(self):
        return self.context
