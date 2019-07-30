from opengever.base.security import elevated_privileges
from opengever.base.utils import get_hostname
from opengever.contact.interfaces import IContactFolder
from plone import api
from plone.memoize import ram
from zope.globalrequest import getRequest


def hostname_cache_key(m, *args, **kwargs):
    return get_hostname(getRequest())


@ram.cache(hostname_cache_key)
def get_contactfolder_url(elevate_privileges=False):
    if elevate_privileges:

        with elevated_privileges():
            result = api.content.find(object_provides=IContactFolder)
    else:
        result = api.content.find(object_provides=IContactFolder)

    if not result:
        raise Exception('Contactfolder is missing, GEVER deployment was not '
                        'correctly set up.')

    return result[0].getURL()
