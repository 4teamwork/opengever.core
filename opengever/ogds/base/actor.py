class Actor(object):

    @classmethod
    def lookup(cls, identifier):
        return ActorLookup(identifier).lookup()


class InboxActor(Actor):
    pass


class ContactActor(Actor):
    pass


class UserActor(Actor):
    pass


class ActorLookup(object):

    def __init__(self, identifier):
        self.identifier = identifier

    def is_inbox(self):
        return self.identifier.startswith('inbox:')

    def is_contact(self, principal):
        return self.identifier.startswith('contact:')

    def is_user(self, principal):
        return ':' not in self.identifier

    def lookup(self):
        if not self.identifier:
            return None

        elif self.is_inbox():
            return InboxActor(self.identifier)

        elif self.is_contact():
            return ContactActor(self.identifier)

        return UserActor(self.identifier)

        elif self.is_contact(principal):
            contact = self.get_contact(principal, check_permissions=True)
            if contact:
                return contact.getURL()
            else:
                return None

        elif self.is_user(principal):
            portal = getSite()
            user = ogds_service().fetch_user(principal)
            if user:
                return '/'.join((portal.portal_url(), '@@user-details',
                                 user.userid))
            else:
                # fallback with acl_users folder
                portal_membership = getToolByName(portal, 'portal_membership')
                member = portal_membership.getMemberById(principal)
                if member:
                    return portal_membership.getMemberById(
                        principal).getHomeUrl()
            return None
