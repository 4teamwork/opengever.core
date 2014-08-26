from Products.ZCatalog.ZCatalog import ZCatalog
from plone import api


CONTACT_TYPE = 'opengever.contact.contact'


class ContactService(object):

    def all_contact_brains(self, ignore_security=True):
        """Returns a catalog result set of contact brains.
        """
        catalog = api.portal.get_tool('portal_catalog')
        query = {'portal_type': CONTACT_TYPE}

        if ignore_security:
            # make catalog query without checking security (allowedRolesAndUsers)
            # since the contacts are not visible for foreign users but should be
            # in the vocabulary anyway...
            brains = ZCatalog.searchResults(catalog, **query)
        else:
            brains = catalog(query)

        return brains
