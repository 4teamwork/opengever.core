from opengever.base.utils import get_hostname
from opengever.contact.interfaces import IContactFolder
from plone import api
from plone.memoize import ram
from zope.globalrequest import getRequest


def hostname_cache_key(m):
    return get_hostname(getRequest())


@ram.cache(hostname_cache_key)
def get_contactfolder_url():
    result = api.content.find(object_provides=IContactFolder)
    if not result:
        raise Exception('Contactfolder is missing, GEVER deployment was not '
                        'correctly set up.')

    return result[0].getURL()
