from plone.restapi.services import Service


class RoleInheritanceGet(Service):

    def reply(self):
        blocked = getattr(self.context, '__ac_local_roles_block__', False)
        return {
            'blocked': blocked
        }

