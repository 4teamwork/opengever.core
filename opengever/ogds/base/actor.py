"""
Given a string-identifier lookup an actor.

Usage:

For a string identifier representing an unknown actor type:
>> Actor.lookup('my-identifier')

The lookup results are
 - A null-implementation if the identifier is None or actor is missing.
 - an InboxActor if the identifier starts with "inbox:"
 - a ContactActor if the identifier starts with "contact:"
 - a TeamActor if the identifier starts with "team:"
 - a CommitteeActor if the identifier starts with "committee:"
 - a PloneUserActor or an OGDSUserActor for any other string.

For known actor types use:
>> Actor.user('my-identifier', user=user)

>> Actor.inbox('my-identifier', org_unit=org_unit)

>> Actor.contact('my-identifier', contact=contact)

"""

from opengever.base.utils import escape_html
from opengever.contact.utils import get_contactfolder_url
from opengever.ogds.base import _
from opengever.ogds.base.browser.userdetails import UserDetails
from opengever.ogds.base.interfaces import IActor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import groupmembers_url
from opengever.ogds.models.service import ogds_service
from opengever.ogds.models.team import Team
from plone import api
from plone.dexterity.utils import safe_unicode
from Products.CMFCore.interfaces._tools import IMemberData
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer


SYSTEM_ACTOR_ID = '__system__'


@implementer(IActor)
class Actor(object):

    css_class = 'actor-user'
    actor_type = 'user'

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
    def group(cls, identifier, group=None):
        lookup = ActorLookup(identifier)
        if not identifier:
            return lookup.create_null_actor()

        return lookup.create_group_actor(group=group)

    @classmethod
    def inbox(cls, identifier, org_unit=None):
        return ActorLookup(identifier).create_inbox_actor(org_unit=org_unit)

    @classmethod
    def contact(cls, identifier, contact=None):
        lookup = ActorLookup(identifier)
        if not identifier:
            return lookup.create_null_actor()

        return lookup.create_contact_actor(contact=contact)

    @classmethod
    def team(cls, identifier, team=None):
        lookup = ActorLookup(identifier)
        if not identifier:
            return lookup.create_null_actor()

        return lookup.create_team_actor(team=team)

    def get_profile_url(self):
        raise NotImplementedError()

    def get_label(self, with_principal=True):
        raise NotImplementedError()

    def get_label_with_admin_unit(self, with_principal=True):
        admin_unit = get_current_admin_unit()
        return admin_unit.prefix_label(
            self.get_label(with_principal=with_principal))

    def get_link(self, with_icon=False):
        url = self.get_profile_url()
        label = escape_html(self.get_label())

        if not url:
            if with_icon:
                return u'<span class="actor-label {}">{}</span>'.format(
                    self.css_class, label)

            return label

        if with_icon:
            link = u'<a href="{}" class="actor-label {}">{}</a>'.format(
                url, self.css_class, label)
        else:
            link = u'<a href="{}">{}</a>'.format(url, label)

        return link

    def corresponds_to(self, user):
        raise NotImplementedError()

    @property
    def permission_identifier(self):
        raise NotImplementedError()

    def represents(self):
        raise NotImplementedError()

    def representatives(self):
        raise NotImplementedError()

    def get_portrait_url(self):
        raise NotImplementedError()


@implementer(IActor)
class NullActor(object):

    actor_type = 'null'

    def __init__(self, identifier):
        self.identifier = identifier

    def corresponds_to(self, user):
        return False

    def get_profile_url(self):
        return None

    def get_label(self, with_principal=True):
        return self.identifier or u''

    def get_link(self, with_icon=False):
        return self.identifier or u''

    def represents(self):
        return None

    def representatives(self):
        return []

    def get_portrait_url(self):
        return None


@implementer(IActor)
class SystemActor(object):
    """Used for system notifications, using the internal SYSTEM_ACTOR_ID.
    """

    actor_type = 'system'

    def __init__(self, identifier):
        if identifier != SYSTEM_ACTOR_ID:
            raise ValueError('System actor use only for the SYSTEM_ACTOR_ID')

        self.identifier = identifier

    def corresponds_to(self, user):
        return False

    def get_profile_url(self):
        return None

    def get_label(self, with_principal=True):
        return u''

    def get_link(self, with_icon=False):
        return u''

    def represents(self):
        return None

    def representatives(self):
        return []

    def get_portrait_url(self):
        return None


@implementer(IActor)
class InboxActor(Actor):

    css_class = 'actor-inbox'
    actor_type = 'inbox'

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

    def representatives(self):
        return self.org_unit.inbox().assigned_users()

    def represents(self):
        return self.org_unit

    def get_portrait_url(self):
        return None


@implementer(IActor)
class TeamActor(Actor):

    css_class = 'actor-team'
    actor_type = 'team'

    def __init__(self, identifier, team=None):
        super(TeamActor, self).__init__(identifier)
        self.team = team

    def get_profile_url(self):
        return '{}/team-{}/view'.format(
            get_contactfolder_url(unrestricted=True), self.team.team_id)

    def corresponds_to(self, user):
        return user in self.team.group.users

    def get_label(self, with_principal=None):
        return self.team.label()

    @property
    def permission_identifier(self):
        return self.team.group.groupid

    def representatives(self):
        return self.team.group.users

    def represents(self):
        return self.team

    def get_portrait_url(self):
        return None


@implementer(IActor)
class CommitteeActor(Actor):

    css_class = 'actor-committee'
    actor_type = 'committee'

    def __init__(self, identifier, committee=None):
        super(CommitteeActor, self).__init__(identifier)
        self.committee = committee

    def get_profile_url(self):
        return self.committee.get_url()

    def corresponds_to(self, user):
        return user in self.representatives()

    def get_label(self, with_principal=None):
        return self.committee.title

    def representatives(self):
        # Avoid circular imports
        from opengever.meeting.activity.helpers import get_users_by_group
        return get_users_by_group(self.committee.group_id)

    def represents(self):
        return self.committee

    def get_portrait_url(self):
        return None


@implementer(IActor)
class ContactActor(Actor):

    css_class = 'actor-contact'
    actor_type = 'contact'

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

    def representatives(self):
        return []

    def represents(self):
        return self.contact

    def get_portrait_url(self):
        return None


@implementer(IActor)
class PloneUserActor(Actor):

    def __init__(self, identifier, user=None):
        super(PloneUserActor, self).__init__(identifier)
        self.user = user

    def corresponds_to(self, user):
        return False

    def get_label(self, with_principal=True):
        name = self.user.getProperty('fullname')
        if not name:
            name = safe_unicode(self.user.getUserName())

        if with_principal:
            return u'{} ({})'.format(safe_unicode(name), safe_unicode(self.identifier))
        else:
            return name

    def get_profile_url(self):
        return self.user.getHomeUrl()

    def representatives(self):
        return []

    def represents(self):
        return self.user

    def get_portrait_url(self):
        portrait = self.user.getPersonalPortrait()
        if portrait:
            return portrait.absolute_url()


@implementer(IActor)
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

    def representatives(self):
        return [self.user]

    def represents(self):
        return self.user

    def get_portrait_url(self):
        mtool = api.portal.get_tool('portal_membership')
        member = mtool.getMemberById(self.user.userid)
        portrait = member.getPersonalPortrait()
        if portrait:
            return portrait.absolute_url()


@implementer(IActor)
class OGDSGroupActor(Actor):

    actor_type = 'group'

    def __init__(self, identifier, group=None):
        super(OGDSGroupActor, self).__init__(identifier)
        self.group = group

    def corresponds_to(self, user):
        return user in self.representatives()

    def get_label(self, with_principal=True):
        return self.group.label()

    def get_profile_url(self):
        return groupmembers_url(self.group.groupid)

    @property
    def permission_identifier(self):
        return self.identifier

    def representatives(self):
        return self.group.users

    def represents(self):
        return self.group

    def get_portrait_url(self):
        return None


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

    def is_team(self):
        return self.identifier.startswith('team:')

    def create_team_actor(self, team=None):
        if not team:
            team = Team.query.get_by_actor_id(self.identifier)

        return TeamActor(self.identifier, team=team)

    def is_committee(self):
        return self.identifier.startswith('committee:')

    def create_committee_actor(self, committee=None):
        from opengever.meeting.model import Committee
        if not committee:
            committee_id = self.identifier.split(':', 1)[1]
            committee = Committee.query.filter_by(committee_id=committee_id).one()

        return CommitteeActor(self.identifier, committee=committee)

    def is_contact(self):
        return self.identifier.startswith('contact:')

    def is_system_actor(self):
        return self.identifier == SYSTEM_ACTOR_ID

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

    def load_group(self):
        return ogds_service().fetch_group(self.identifier)

    def create_group_actor(self, group=None):
        if not group:
            group = self.load_group()
        if group:
            return OGDSGroupActor(self.identifier, group=group)
        else:
            return self.create_null_actor()

    def create_null_actor(self):
        return NullActor(self.identifier)

    def create_system_actor(self):
        return SystemActor(self.identifier)

    def lookup(self):
        if not self.identifier:
            return self.create_null_actor()

        elif self.is_system_actor():
            return self.create_system_actor()

        elif self.is_inbox():
            return self.create_inbox_actor()

        elif self.is_contact():
            return self.create_contact_actor()

        elif self.is_team():
            return self.create_team_actor()

        elif self.is_committee():
            return self.create_committee_actor()

        user = self.load_user()
        if user:
            return self.create_user_actor(user)

        group = self.load_group()
        if group:
            return self.create_group_actor(group)

        return self.create_null_actor()
