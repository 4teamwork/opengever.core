from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from ftw.tabbedview.interfaces import ITabbedView


def opengever_tabbedview_configuration(context):
    """Update the ftw.tabbedview configuration in the registry:
    - Activate dynamic batching for listing views.
    """
    registry = getUtility(IRegistry)

    try:
        tabbedview_configuration = registry.forInterface(ITabbedView)
    except KeyError:
        # The registry entry doesn't exist yet
        return
    tabbedview_configuration.dynamic_batchsize_enabled = True
