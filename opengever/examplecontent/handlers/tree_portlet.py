
from zope.component import getUtility, getAdapter, getMultiAdapter

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager

from opengever.portlets.tree import treeportlet

class SetupVarious(object):

    def __call__(self, setup):
        self.setup = setup
        self.portal = self.setup.getSite()
        self.openDataFile = self.setup.openDataFile
        repository_root = self.portal.get('ordnungssystem')
        self.register_portlet(
            repository_root,
            u'plone.leftcolumn',
            'tree',
            treeportlet.Assignment,
            )

    def register_portlet(self, context, column_name, key, assignment, **kw):
        if not context:
            return
        column = getUtility(IPortletManager, name=column_name)
        mapping = getMultiAdapter((context, column), IPortletAssignmentMapping)
        if key not in mapping:
            mapping[key] = assignment(**kw)

