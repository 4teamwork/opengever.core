from plone.locking.interfaces import IRefreshableLockable
from Products.Five.browser import BrowserView
from zope.component import queryAdapter


# The ploneform-macros view


class Macros(BrowserView):

    def __getitem__(self, key):
        return self.index.macros[key]

    def enable_refreshable_locks(self):
        return bool(queryAdapter(self.context, IRefreshableLockable))
