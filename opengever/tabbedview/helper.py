from zope.component import getUtility
from plone.memoize import ram

from opengever.octopus.tentacle.interfaces import IContactInformation


@ram.cache(lambda m,i,author: author)
def readable_ogds_author(item, author):
    info = getUtility(IContactInformation)
    return info.render_link(author)
