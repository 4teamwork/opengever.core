
from zope.component import getUtility, getAdapter, getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager

from plone.app.portlets.portlets import navigation

class SetupVarious(object):

    def __call__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        self.register_portlet(
            self.portal,
            u'plone.leftcolumn',
            'navigation',
            navigation.Assignment,
            topLevel = 0,
            bottomLevel = 1,
            )

    def register_portlet(self, context, column_name, key, assignment, **kw):
        if not context:
            return
        column = getUtility(IPortletManager, name=column_name)
        mapping = getMultiAdapter((context, column), IPortletAssignmentMapping)
        if key not in mapping:
            mapping[key] = assignment(**kw)

