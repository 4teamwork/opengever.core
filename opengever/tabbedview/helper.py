from zope.component import getUtility
from plone.memoize import ram

from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.CMFCore.interfaces._tools import IMemberData

from opengever.octopus.tentacle.interfaces import IContactInformation


@ram.cache(lambda m,i,author: author)
def readable_ogds_author(item, author):
    if IPropertiedUser.providedBy(author) or IMemberData.providedBy(author):
        author = author.getId()
    info = getUtility(IContactInformation)
    return info.render_link(author)
