from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from izug.basetheme.interfaces import ISiteProperties

def set_application_title(context):
    """ Set the application title for GEVER.
    (used in the live search box)
    """
    registry = getUtility(IRegistry)

    try:
        site_properties = registry.forInterface(ISiteProperties)
    except KeyError:
        # The registry entry doesn't exist yet
        return

    site_properties.application_title = u'GEVER'



