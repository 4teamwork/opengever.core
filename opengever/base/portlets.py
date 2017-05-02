from plone.app.portlets.portlets import navigation
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility


def block_context_portlet_inheritance(obj):
    """Block inherited context portlets on given object, in the left column.
    """
    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=obj)
    assignable = getMultiAdapter(
        (obj, manager), ILocalPortletAssignmentManager)
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, True)

    
def add_navigation_portlet_assignment(obj, **kwargs):
    """Add a new navigation portlet to given object to the left column."""

    manager = getUtility(
        IPortletManager, name=u'plone.leftcolumn', context=obj)
    mapping = getMultiAdapter((obj, manager), IPortletAssignmentMapping)
    mapping['navigation'] = navigation.Assignment(**kwargs)
