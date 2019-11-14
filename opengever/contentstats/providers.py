from collections import Counter
from ftw.contentstats.interfaces import IStatsProvider
from ftw.contentstats.providers.portal_types import PortalTypesProvider
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.document.document import Document
from opengever.mail.mail import OGMail
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IStatsProvider)
@adapter(IPloneSiteRoot, IOpengeverBaseLayer)
class GEVERPortalTypesProvider(PortalTypesProvider):
    """Customization of the default ftw.contentstats `portal_types` provider
    that sums up (Documents + Mails) as a separate, fake portal_type
    _opengever.document.behaviors.IBaseDocument for easier processing in ELK.
    """

    def get_raw_stats(self):
        """Return a list of dicts (keys: name, amount).
        """
        counts = super(GEVERPortalTypesProvider, self).get_raw_stats()
        mails = counts.get('ftw.mail.mail', 0)
        docs = counts.get('opengever.document.document', 0)
        counts['_opengever.document.behaviors.IBaseDocument'] = (docs + mails)
        counts['_opengever.dossier.maindossier'] = self.get_main_dossiers_count()
        return counts

    def get_main_dossiers_count(self):
        catalog = api.portal.get_tool('portal_catalog')
        count = len(catalog.unrestrictedSearchResults(
            object_provides=['opengever.dossier.behaviors.dossier.IDossierMarker'],
            is_subdossier=False))
        return count


@implementer(IStatsProvider)
@adapter(IPloneSiteRoot, Interface)
class CheckedOutDocsProvider(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def title(self):
        """Human readable title
        """
        return u'Checked out documents statistics'

    def get_display_names(self):
        return None

    def get_raw_stats(self):
        """Return a dictionary with counts of checked in vs. checked out docs.
        """
        counts = {'checked_out': 0, 'checked_in': 0}
        catalog = api.portal.get_tool('portal_catalog')
        index = catalog._catalog.indexes['checked_out']

        for key in index.uniqueValues():
            t = index._index.get(key)
            if not isinstance(t, int):
                num_docs = len(t)
            else:
                num_docs = 1

            if key == '':
                counts['checked_in'] += num_docs
            else:
                counts['checked_out'] += num_docs

        return counts


@implementer(IStatsProvider)
@adapter(IPloneSiteRoot, Interface)
class FileMimetypesProvider(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def title(self):
        """Human readable title
        """
        return u'File mimetype statistics'

    def get_display_names(self):
        return None

    def get_raw_stats(self):
        """Return a dictionary with counts of file mimetypes.
        """
        counts = {}
        catalog = api.portal.get_tool('portal_catalog')

        # Documents
        docs_query = {
            'portal_type': 'opengever.document.document',
            'review_state': Document.active_state,
            'trashed': False,
        }
        docs = catalog.unrestrictedSearchResults(docs_query)

        docs_counts = Counter([b.getContentType for b in docs])
        counts.update(docs_counts)

        # Mails
        mails_query = {
            'portal_type': 'ftw.mail.mail',
            'review_state': OGMail.active_state,
            'trashed': False,
        }
        mails = catalog.unrestrictedSearchResults(mails_query)
        counts['message/rfc822'] = len(mails)

        # Drop mimetype key of empty string (if present). This entry can
        # result from documents without files. We need to drop this because
        # several components in the ELK stack (filebeat, elasticsearch) can't
        # deal with empty JSON keys gracefully, and choke on them.
        counts.pop('', None)

        return counts
