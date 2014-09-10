"""
Given a string-identifier lookup an actor.

Usage:

For a string identifier representing an unknown actor type:
>> Actor.lookup('my-identifier')

The lookup results are
 - A null-implementation if the identifier is None or actor is missing.
 - an InboxActor if the identifier starts with "inbox:"
 - a ContactActor if the identifier starts with "contact:"
 - an UserActor for any other string

For known actor types use:
>> Actor.user('my-identifier', user=user)

>> Actor.inbox('my-identifier', org_unit=org_unit)

>> Actor.contact('my-identifier', contact=contact)

"""

from opengever.ogds.base import _
from opengever.ogds.base.browser.userdetails import UserDetails
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.interfaces._tools import IMemberData
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
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
    def user(cls, identifier, user=None):
        lookup = ActorLookup(identifier)
        if not identifier:
            return lookup.create_null_actor()

        return lookup.create_user_actor(user=user)

    @classmethod
    def inbox(cls, identifier, org_unit=None):
        return ActorLookup(identifier).create_inbox_actor(org_unit=org_unit)

    @classmethod
    def contact(cls, identifier, contact=None):
        lookup = ActorLookup(identifier)
        if not identifier:
            return lookup.create_null_actor()

        return lookup.create_contact_actor(contact=contact)

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

        return u'<a href="{}">{}</a>'.format(url, label)

    def corresponds_to(self, user):
        raise NotImplementedError()

    @property
    def permission_identifier(self):
        raise NotImplementedError()


class NullActor(object):

    def __init__(self, identifier):
        self.identifier = identifier

    def corresponds_to(self, user):
        return False

    def get_profile_url(self):
        return None

    def get_label(self, with_principal=True):
        return self.identifier or u''

    def get_link(self):
        return self.identifier or u''


class InboxActor(Actor):

    def __init__(self, identifier, org_unit=None):
        super(InboxActor, self).__init__(identifier)
        self.org_unit = org_unit

    def get_profile_url(self):
        return None

    def corresponds_to(self, user):
        return user in self.org_unit.inbox().assigned_users()

    def get_label(self, with_principal=None):
        # we need to instantly translate, because otherwise
        # stuff like the autocomplete widget will not work
        # properly.
        label = _(u'inbox_label',
                  default=u'Inbox: ${client}',
                  mapping=dict(client=self.org_unit.label()))

        return translate(label, context=getRequest())

    @property
    def permission_identifier(self):
        return self.org_unit.inbox_group.groupid


class ContactActor(Actor):

    def __init__(self, identifier, contact=None):
        super(ContactActor, self).__init__(identifier)
        self.contact = contact

    def corresponds_to(self, user):
        return False

    def get_label(self, with_principal=True):
        if self.contact.lastname or self.contact.firstname:
            name = ' '.join(name for name in
                           (self.contact.lastname, self.contact.firstname) if name)
        else:
            name = self.contact.id

        if with_principal and self.contact.email:
            return u'{} ({})'.format(name, self.contact.email)
        else:
            return name

    def get_profile_url(self):
        return self.contact.getURL()


class PloneUserActor(Actor):

    def __init__(self, identifier, user=None):
        super(PloneUserActor, self).__init__(identifier)
        self.user = user

    def corresponds_to(self, user):
        return False

    def get_label(self, with_principal=True):
        name = self.user.getProperty('fullname')
        if not name:
            name = self.user.getUserName()

        if with_principal:
            return u'{} ({})'.format(name, self.identifier)
        else:
            return name

    def get_profile_url(self):
        return self.user.getHomeUrl()


class OGDSUserActor(Actor):

    def __init__(self, identifier, user=None):
        super(OGDSUserActor, self).__init__(identifier)
        self.user = user

    def corresponds_to(self, user):
        return self.user == user

    def get_label(self, with_principal=True):
        return self.user.label(with_principal=with_principal)

    def get_profile_url(self):
        return UserDetails.url_for(self.user.userid)

    @property
    def permission_identifier(self):
        return self.identifier


class ActorLookup(object):

    def __init__(self, identifier):
        self.identifier = identifier

    def is_inbox(self):
        return self.identifier.startswith('inbox:')

    def create_inbox_actor(self, org_unit=None):
        if not org_unit:
            org_unit_id = self.identifier.split(':', 1)[1]
            org_unit = ogds_service().fetch_org_unit(org_unit_id)
            assert org_unit, 'OrgUnit {} for identifier {} is missing.'.format(
                org_unit_id, self.identifier)

        return InboxActor(self.identifier, org_unit=org_unit)

    def is_contact(self):
        return self.identifier.startswith('contact:')

    def create_contact_actor(self, contact=None):
        if not contact:

            catalog = getToolByName(getSite(), 'portal_catalog')
            query = {'portal_type': 'opengever.contact.contact',
                     'contactid': self.identifier}

            contacts = catalog.searchResults(**query)

            if len(contacts) == 0:
                return self.create_null_actor()

            contact = contacts[0]

        return ContactActor(self.identifier, contact=contact)

    def is_plone_user(self, user):
        return IPropertiedUser.providedBy(user) or IMemberData.providedBy(user)

    def load_user(self):
        user = ogds_service().fetch_user(self.identifier)
        if not user:
            portal = getSite()
            portal_membership = getToolByName(portal, 'portal_membership')
            user = portal_membership.getMemberById(self.identifier)

        return user

    def create_user_actor(self, user=None):
        if not user:
            user = self.load_user()

        if user:
            if self.is_plone_user(user):
                return PloneUserActor(self.identifier, user=user)
            else:
                return OGDSUserActor(self.identifier, user=user)
        else:
            return self.create_null_actor()

    def create_null_actor(self):
        return NullActor(self.identifier)

    def lookup(self):
        if not self.identifier:
            return self.create_null_actor()

        elif self.is_inbox():
            return self.create_inbox_actor()

        elif self.is_contact():
            return self.create_contact_actor()

        return self.create_user_actor()
