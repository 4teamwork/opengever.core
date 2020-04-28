from plone.restapi.services import Service
from Products.CMFPlone.CatalogTool import allowedRolesAndUsers


class AllowedRolesAndPrincipalsGet(Service):
    """API Endpoint (callable on every context) which returns the information which roles,
    groups or users are allowed to view an object.

    GET /(path)/@allowed-roles-and-principals HTTP/1.1
    """

    def reply(self):
        allowed_roles_and_users = allowedRolesAndUsers(self.context)()
        allowed_roles_and_users = [principal.replace(
            'user:', 'principal:') for principal in allowed_roles_and_users]
        return {
            '@id': '/'.join((self.context.absolute_url(), '@allowed-roles-and-principals')),
            "allowed_roles_and_principals": allowed_roles_and_users
        }
