from ftw.tabbedview.interfaces import ITabbedView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def installed(site):
    """Update the ftw.tabbedview configuration in the registry:
       - Activate dynamic batching for listing views.

    """
    registry = getUtility(IRegistry)
    tabbedview_configuration = registry.forInterface(ITabbedView)
    tabbedview_configuration.dynamic_batchsize_enabled = True
