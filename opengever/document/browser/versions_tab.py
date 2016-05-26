from Acquisition import aq_parent
from datetime import datetime
from five import grok
from ftw.table.interfaces import ITableSource
from ftw.table.interfaces import ITableSourceConfig
from opengever.base.protect import unprotected_write
from opengever.document import _
from opengever.document.browser.download import DownloadConfirmationHelper
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.ogds.base.actor import Actor
from opengever.tabbedview import BaseListingTab
from opengever.tabbedview import GeverTableSource
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.CMFPlone.utils import safe_unicode
from zope.component import getMultiAdapter
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
    link_text = translate_text(label)

    klass = u''
    if css_class:
        klass = u'class="{}"'.format(safe_unicode(css_class))

    link = u'<a href="{}" {}>{}</a>'.format(
        safe_unicode(url), klass, link_text)
    return link


def translate_text(text):
    return translate(text, domain='opengever.document', context=getRequest())


class VersionDataProxy(object):
    """A proxy for CMFEditions `VersionData` dicts as returned by
    ShadowHistory.retrieve().

    This represents the metadata for a single version of a particular object.

    This proxy object provides easier attribute access to some of the
    VersionData's metadata, so we can use decent column names in the
    VersionsTab below.

    It also provides some helper methods for building data that ends up in
    the columns but isn't directly accessible.
    """

    def __init__(self, version_data, url, is_revert_allowed):
        self._version_data = version_data
        self._url = url
        self._is_revert_allowed = is_revert_allowed

    def __getattr__(self, name):
        """Proxy dotted attribute access to the corresponding value in the
        wrapped _version_data dictionary
        """
        if name in ('__iter__', '__contains__', '__getitem__'):
            # We're wrapping a dict, but we want to provide dotted attribute
            # access instead of exposing the dict interface - we therefore
            # don't support iteration, membership testing or subscription.
            raise AttributeError(name)

        return self._version_data.get(name)

    @property
    def sys_metadata(self):
        return self._version_data['metadata']['sys_metadata']

    @property
    def is_revert_allowed(self):
        return self._is_revert_allowed

    @property
    def url(self):
        """Absolute URL of the object that this version belongs to.
        """
        return self._url

    @property
    def version(self):
        """The ID ("number") of this version.
        """
        return self._version_data['version_id']

    @property
    def actor(self):
        """Returns a formatted link to the actor that created this version.
        """
        principal = self.sys_metadata['principal']
        actor = Actor.user(principal)
        return actor.get_link()

    @property
    def timestamp(self):
        """Creation timestamp of this version, formatted as localized time.
        """
        ts = self.sys_metadata['timestamp']
        dt = datetime.fromtimestamp(ts)
        return api.portal.get_localized_time(datetime=dt, long_format=True)

    @property
    def comment(self):
        """Comment for this version.
        """
        return self.sys_metadata['comment']

    @property
    def download_link(self):
        """Returns a formatted link that allows to download a copy of this
        version (opens in an overlay).
        """
        dc_helper = DownloadConfirmationHelper()
        link = dc_helper.get_html_tag(
            self.url,
            url_extension="?version_id=%s" % self.version,
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
        """Returns a formatted link to revert to this particular version if
        reverting is allowed, an inactive label otherwise.
        """

        if self.is_revert_allowed:
            url = '{}/revert-file-to-version?version_id={}'
            url = url.format(self.url, self.version_id)
            url = addTokenToUrl(url)
            link = translate_link(
                url, _(u'label_reset', default=u'reset'),
                css_class='standalone function-revert')
            return link
        else:
            label = translate_text(_(u'label_reset', default=u'reset'))
            return u'<span class="discreet">{}</span>'.format(label)


class LazyHistoryMetadataProxy(object):
    """A proxy for CMFEditions `ShadowHistory` objects as returned by
    getHistoryMetadata().

    This proxy wraps a ShadowHistory and provides lazy access to the
    underlying version datas. Returned version datas are wrapped in a
    VersionDataProxy for easier use in table columns.

    All we need to do here to ensure lazy access and batching is to provide
    two interfaces:

    - __len__() to get the total length of the version history and caluclate
      number of batch pages etc.
    - __getitem__() to access version data for a specific version

    There's no need for iteration. Given those two interfaces, plone.batching
    is able to do the rest and provide lazy batched access.

    See plone.batching.batch.BaseBatch.__getitem__() for details.
    """

    def __init__(self, history, url, is_revert_allowed=False):
        self._history = history
        self._length = history.getLength(countPurged=False)

        self._url = url
        self._is_revert_allowed = is_revert_allowed

    def __len__(self):
        """Returns the total number of versions
        """
        return self._length

    def __getitem__(self, index):
        """Returns the version data for the version at `index`, where index
        is the position in a descending list (most recent first, oldest
        version last).

        This allows for easy use in listing without having to mess with
        reversing the sort order.

        See Products.CMFEditions.browser.diff.DiffView.__call__()
        for a more detailed example on how to use the ShadowHistory API.
        """
        # Order versions descending (most recent first)
        # CMFEditions' storages call this the "selector" - it's basically the
        # internal version number, with the low values being old versions
        selector = self._length - index - 1

        version_id = self._history.getVersionId(selector, countPurged=False)
        vdata = self._history.retrieve(selector, countPurged=False)
        vdata['version_id'] = version_id
        return VersionDataProxy(vdata, self._url, self._is_revert_allowed)


class IVersionsSourceConfig(ITableSourceConfig):
    """
    """


class VersionsTableSource(GeverTableSource):
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
        shadow_history = repo_tool.getHistoryMetadata(obj)
        manager = getMultiAdapter((obj, self.request), ICheckinCheckoutManager)

        return LazyHistoryMetadataProxy(
            shadow_history, obj.absolute_url(),
            is_revert_allowed=manager.is_revert_allowed())


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
