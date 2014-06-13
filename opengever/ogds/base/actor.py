"""
Given a string-identifier lookup an actor.

#XXX TODO: describe where we use actors.

Usage:
>> Actor.lookup('my-identifier')

The lookup results are
 - an InboxActor if the identifier starts with "inbox:"
 - a ContactActor if the identifier starts with "contact:"
 - an UserActor for any other string not containing a colon
 - A null-implementation if the identifier is None

"""
from opengever.ogds.base import _
from opengever.ogds.base.browser.userdetails import UserDetails
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate


class Actor(object):

    def __init__(self, identifier):
        self.identifier = identifier

    @classmethod
    def lookup(cls, identifier):
        return ActorLookup(identifier).lookup()

    @classmethod
    def user(cls, identifier):
        if not identifier:
            return NullActor()
        assert ActorLookup(identifier).is_user()
        return UserActor(identifier)

    @classmethod
    def inbox(cls, identifier):
        if not identifier:
            return NullActor()
        assert ActorLookup(identifier).is_inbox()
        return InboxActor(identifier)

    @classmethod
    def contact(cls, identifier):
        if not identifier:
            return NullActor()
        assert ActorLookup(identifier).is_contact()
        return ContactActor(identifier)

    def get_profile_url(self):
        raise NotImplementedError()

    def get_label(self, with_principal=True):
        raise NotImplementedError()

    def get_label_with_admin_unit(self, with_principal=True):
        admin_unit = get_current_admin_unit()
        return admin_unit.prefix_label(
            self.get_label(with_principal=with_principal))

    def get_link(self):
        url = self.get_profile_url()
        label = self.get_label()

        if not url:
            return label

        return '<a href="{}">{}</a>'.format(url, label)


class NullActor(object):

    def get_profile_url(self):
        return None

    def get_label(self, with_principal=True):
        return ''

    def get_link(self):
        return None


class InboxActor(Actor):

    def __init__(self, identifier, org_unit=None):
        super(InboxActor, self).__init__(identifier)
        self._org_unit = org_unit

    def get_profile_url(self):
        return None

    def get_label(self):
        org_unit = self.load_org_unit()
        # we need to instantly translate, because otherwise
        # stuff like the autocomplete widget will not work
        # properly.
        label = _(u'inbox_label',
                  default=u'Inbox: ${client}',
                  mapping=dict(client=org_unit.label()))

        return translate(label, context=getRequest())

    def load_org_unit(self):
        if not self._org_unit:
            org_unit_id = self.identifier.split(':', 1)[1]
            self._org_unit = ogds_service().fetch_org_unit(org_unit_id)
        return self._org_unit


class ContactActor(Actor):

    def __init__(self, identifier, contact=None):
        super(ContactActor, self).__init__(identifier)
        self._contact = contact

    def load(self):
        if not self._contact:
            catalog = getToolByName(getSite(), 'portal_catalog')
            query = {'portal_type': 'opengever.contact.contact',
                     'contactid': self.identifier}

            contacts = catalog.searchResults(**query)

            if len(contacts) == 0:
                return None
            else:
                self._contact = contacts[0]
        return self._contact

    def get_label(self, with_principal=True):
        contact = self.load()
        if not contact:
            return self.identifier

        if contact.lastname or contact.firstname:
            name = ' '.join(name for name in
                           (contact.lastname, contact.firstname) if name)
        else:
            name = contact.id

        if with_principal and contact.email:
            return '{} ({})'.format(name, contact.email)
        else:
            return name

    def get_profile_url(self):
        contact = self.load()
        if contact:
            return contact.getURL()
        else:
            return None


class UserActor(Actor):

    def __init__(self, identifier, user=None):
        super(UserActor, self).__init__(identifier)
        self._user = user

    def load(self):
        if not self._user:
            user = ogds_service().fetch_user(self.identifier)
            if user:
                self._user = _OGDSUser(user)
            else:
                portal = getSite()
                portal_membership = getToolByName(portal, 'portal_membership')
                member = portal_membership.getMemberById(self.identifier)
                if member:
                    self._user = _PloneUser(member)

        return self._user

    def get_profile_url(self):
        user = self.load()
        if user:
            return user.get_profile_url()
        return None

    def get_label(self, with_principal=True):
        user = self.load()
        if user:
            return user.get_label(with_principal)
        return None


class _PloneUser(object):

    def __init__(self, plone_user):
        self.user = plone_user

    def get_label(self, with_principal=True):
        if self.user.lastname or self.user.firstname:
            name = ' '.join(name for name in
                           (self.user.lastname, self.user.firstname) if name)
        else:
            name = self.user.userid

        if with_principal:
            return u'{} ({})'.format(name, self.user.userid)
        else:
            return name

    def get_profile_url(self):
        return self.user.getHomeUrl()


class _OGDSUser(object):

    def __init__(self, ogds_user):
        self.ogds_user = ogds_user

    def get_label(self, with_principal=True):
        return self.ogds_user.label(with_principal=with_principal)

    def get_profile_url(self):
        return UserDetails.url_for(self.ogds_user.userid)


class ActorLookup(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def is_inbox(self):
        return self.identifier.startswith('inbox:')

    def is_contact(self):
        return self.identifier.startswith('contact:')

    def is_user(self):
        return ':' not in self.identifier

    def lookup(self):
        if not self.identifier:
            return NullActor()

        elif self.is_inbox():
            return InboxActor(self.identifier)

        elif self.is_contact():
            return ContactActor(self.identifier)

        return UserActor(self.identifier)
