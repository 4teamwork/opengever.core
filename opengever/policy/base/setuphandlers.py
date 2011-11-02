from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from izug.basetheme.browser.interfaces import ISearchText

def search_string(context):
    """ Set the searchstring for izug"""
    registry = getUtility(IRegistry)

    try:
        first_part = registry.forInterface(ISearchText)
    except KeyError:
        return

    first_part.searchtext = u'Gever'



