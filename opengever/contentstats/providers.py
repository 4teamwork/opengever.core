from ftw.contentstats.interfaces import IStatsProvider
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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
