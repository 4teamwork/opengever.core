from opengever.base.model import create_session
from opengever.contact.service import CONTACT_TYPE
from opengever.ogds.base import _
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.query import extend_query_with_textfilter
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from plone import api
from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy.sql.expression import asc
from z3c.formwidget.query.interfaces import IQuerySource
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class AllUsersInboxesAndTeamsSource(object):
    """This example of a IQuerySource is taken from the
    plone.formwidget.autocomplete
    """

    def __init__(self, context, **kwargs):
        self.context = context
        self.terms = []
        self.client_id = self.get_client_id()

        self.only_current_orgunit = kwargs.get('only_current_orgunit', False)
        self.only_current_inbox = kwargs.get('only_current_inbox', False)
        self.include_teams = kwargs.get('include_teams', False)

    @property
    def only_users(self):
        return False

    @property
    def base_query(self):
        """A base query which joins the user and orgunits together and also
        filters the query based on some options:
            - only_users: Decide if only the user model will be returned
            - only_current_orgunit: Decide if only the current Orgunit will
              be queried.

        The base_query also filtes results from disabled orgunits by default.
        """
        models = (User, ) if self.only_users else (User, OrgUnit)
        query = create_session().query(*models) \
                                .join(OrgUnit.users_group) \
                                .join(Group.users)
        query = query.filter(OrgUnit.enabled == True)

        if self.only_current_orgunit:
            query = query.filter(OrgUnit.unit_id == self.client_id)

        return query

    def __contains__(self, value):
        token = value
        try:
            self.getTermByToken(token)
        except LookupError:
            return False

        return True

    def __iter__(self):
        return self.terms.__iter__()

    def __len__(self):
        return len(self.terms)

    def getTerm(self, value):

        data = value.split(':', 1)
        if len(data) == 2:
            orgunit_id, userid = data
        else:
            userid = value
            orgunit_id = self.client_id

        # Handle special case - Inboxes: in form "inbox:unit_id"
        if ActorLookup(value).is_inbox():
            orgunit_id = userid
            query = OrgUnit.query

            if self.only_current_inbox:
                orgunit = query.filter(OrgUnit.unit_id == self.client_id) \
                               .filter(OrgUnit.unit_id == orgunit_id) \
                               .one()
            else:
                orgunit = query.filter(OrgUnit.unit_id == orgunit_id) \
                               .one()

            value = token = orgunit.inbox().id()
            title = translate(_(u'inbox_label',
                                default=u'Inbox: ${client}',
                                mapping=dict(client=orgunit.label())),
                              context=getRequest())

            return SimpleTerm(value, token, title)

        if ActorLookup(value).is_team():
            if not self.include_teams:
                raise LookupError

            team = Team.query.get_by_actor_id(value)
            return SimpleTerm(team.actor_id(), team.actor_id(), team.label())

        user, orgunit = self.base_query.filter(OrgUnit.unit_id == orgunit_id) \
                                       .filter(User.userid == userid).one()

        token = u'{}:{}'.format(orgunit_id, userid)
        title = u'{}: {} ({})'.format(orgunit.title,
                                      user.fullname(),
                                      user.userid)
        return SimpleTerm(value, token, title)

    def getTermByToken(self, token):
        """ Should raise LookupError if term could not be found.
        Check zope.schema.interfaces.IVocabularyTokenized
        """
        orgunit_id, userid = (None, None)

        if not token:
            raise LookupError('A token "unit_id:userid" is required.')

        try:
            orgunit_id, userid = token.split(':', 1)
        except ValueError:
            raise LookupError('A token "unit_id:userid" is required.')

        try:
            value = token
            return self.getTerm(value)
        except orm.exc.NoResultFound:
            raise LookupError

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.base_query,
            [OrgUnit.title, OrgUnit.unit_id,
             User.userid, User.firstname, User.lastname, User.email],
            text_filters)

        query = query.filter_by(active=True)
        query = query.order_by(asc(func.lower(User.lastname)),
                               asc(func.lower(User.firstname)))

        for user, orgunit in query:
            self.terms.append(
                self.getTerm(u'{}:{}'.format(orgunit.id(), user.userid)))

        self._extend_terms_with_inboxes(text_filters)
        if self.include_teams:
            self._extend_terms_with_teams(text_filters)

        return self.terms

    def _extend_terms_with_inboxes(self, text_filters):
        inbox_text = translate(_(u'inbox_label',
                                 default=u'Inbox: ${client}',
                                 mapping=dict(client='')),
                               context=getRequest()).strip().lower()

        text_filters = filter(lambda text: text.lower() not in inbox_text,
                              text_filters)

        query = OrgUnit.query
        query = query.filter(OrgUnit.enabled == True)

        if self.only_current_inbox:
            query = query.filter(OrgUnit.unit_id == self.client_id)

        query = extend_query_with_textfilter(
            query,
            [OrgUnit.title, OrgUnit.unit_id],
            text_filters)

        for orgunit in query:
            self.terms.insert(0, self.getTerm(orgunit.inbox().id()))

    def _extend_terms_with_teams(self, text_filters):
        query = Team.query.filter(Team.active == True)
        query = extend_query_with_textfilter(query, [Team.title], text_filters)

        for team in query:
            self.terms.insert(0, self.getTerm(team.actor_id()))

    def get_client_id(self):
        """Tries to get the client from the request. If no client is found None
        is returned.
        """

        request = getRequest()
        client_id = request.get('client',
                                request.get('form.widgets.responsible_client',
                                            getattr(self.context,
                                                    'responsible_client',
                                                    None)))

        if not client_id:
            return None
        elif type(client_id) in (list, tuple, set):
            return client_id[0]
        else:
            return client_id


@implementer(IContextSourceBinder)
class AllUsersInboxesAndTeamsSourceBinder(object):

    def __init__(self,
                 only_current_orgunit=False,
                 only_current_inbox=False,
                 include_teams=False):

        self.only_current_orgunit = only_current_orgunit
        self.only_current_inbox = only_current_inbox
        self.include_teams = include_teams

    def __call__(self, context):
        return AllUsersInboxesAndTeamsSource(
            context,
            only_current_orgunit=self.only_current_orgunit,
            only_current_inbox=self.only_current_inbox,
            include_teams=self.include_teams)


@implementer(IQuerySource)
class UsersContactsInboxesSource(AllUsersInboxesAndTeamsSource):

    @property
    def only_users(self):
        return True

    def getTerm(self, value, brain=None):
        # Contacts
        if ActorLookup(value).is_contact() and brain is None:
            catalog = api.portal.get_tool('portal_catalog')
            brain = catalog.unrestrictedSearchResults(
                portal_type=CONTACT_TYPE,
                contactid=value)[0]

        if brain and ActorLookup(value).is_contact():
            actor = Actor.contact(brain.contactid, contact=brain)
            token = value
            title = actor.get_label()
            return SimpleTerm(value, token, title)

        # Inboxes
        if ActorLookup(value).is_inbox():
            orgunit_id = value.split(':', 1)[1]
            orgunit = OrgUnit.query.filter(OrgUnit.unit_id == orgunit_id).one()

            value = token = orgunit.inbox().id()
            title = translate(_(u'inbox_label',
                                default=u'Inbox: ${client}',
                                mapping=dict(client=orgunit.label())),
                              context=getRequest())

            return SimpleTerm(value, token, title)

        user = self.base_query.filter(User.userid == value).one()

        token = value
        title = u'{} ({})'.format(user.fullname(),
                                  user.userid)
        return SimpleTerm(value, token, title)

    def getTermByToken(self, token):
        """ Should raise LookupError if term could not be found.
        Check zope.schema.interfaces.IVocabularyTokenized
        """
        if not token:
            raise LookupError('Expect a userid')

        try:
            value = token
            return self.getTerm(value)
        except (IndexError, orm.exc.NoResultFound):
            raise LookupError

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.base_query,
            [User.userid, User.firstname, User.lastname, User.email],
            text_filters)

        query = query.filter_by(active=True)
        query = query.order_by(asc(func.lower(User.lastname)),
                               asc(func.lower(User.firstname)))

        for user in query:
            self.terms.append(
                self.getTerm(u'{}'.format(user.userid)))

        self._extend_terms_with_contacts(query_string)
        self._extend_terms_with_inboxes(text_filters)
        return self.terms

    def _extend_terms_with_contacts(self, query_string):
        catalog = api.portal.get_tool('portal_catalog')

        if not query_string.endswith('*'):
            query_string += '*'

        query = {'portal_type': CONTACT_TYPE,
                 'SearchableText': query_string}

        for brain in catalog.unrestrictedSearchResults(**query):
            self.terms.append(self.getTerm(brain.contactid, brain))


@implementer(IContextSourceBinder)
class UsersContactsInboxesSourceBinder(object):

    def __call__(self, context):
        return UsersContactsInboxesSource(context)


@implementer(IQuerySource)
class AllUsersSource(AllUsersInboxesAndTeamsSource):
    """Vocabulary of all users assigned to the current admin unit.
    """

    @property
    def search_only_active_users(self):
        return False

    @property
    def only_users(self):
        return True

    def getTermByToken(self, token):

        if not token:
            raise LookupError('A token "userid" is required.')

        try:
            value = token
            return self.getTerm(value)
        except orm.exc.NoResultFound:
            raise LookupError

    def getTerm(self, value):
        user = self.base_query.filter(User.userid == value).one()

        token = value
        title = u'{} ({})'.format(user.fullname(),
                                  user.userid)
        return SimpleTerm(value, token, title)

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.base_query,
            [User.userid, User.firstname, User.lastname, User.email],
            text_filters)

        if self.search_only_active_users:
            query = query.filter_by(active=True)

        query = query.order_by(asc(func.lower(User.lastname)),
                               asc(func.lower(User.firstname)))

        for user in query:
            self.terms.append(
                self.getTerm(u'{}'.format(user.userid)))
        return self.terms


@implementer(IContextSourceBinder)
class AllUsersSourceBinder(object):

    def __call__(self, context):
        return AllUsersSource(context)


@implementer(IQuerySource)
class AssignedUsersSource(AllUsersSource):
    """Vocabulary of all users assigned to the current admin unit.
    """

    @property
    def search_only_active_users(self):
        return True

    @property
    def base_query(self):
        admin_unit = get_current_admin_unit()
        return create_session().query(User) \
            .filter(User.userid == groups_users.columns.userid) \
            .filter(groups_users.columns.groupid == OrgUnit.users_group_id) \
            .filter(OrgUnit.admin_unit_id == admin_unit.unit_id) \
            .filter(OrgUnit.enabled == True)


@implementer(IContextSourceBinder)
class AssignedUsersSourceBinder(object):

    def __call__(self, context):
        return AssignedUsersSource(context)


@implementer(IQuerySource)
class AllEmailContactsAndUsersSource(UsersContactsInboxesSource):
    """Source of all users and contacts with all email addresses.

    Format:
    token = mail-address:id eg. hugo@boss.ch:hugo.boss
    title for users = Fullname (userid, address), eg. Hugo Boss (hugo.boss, hugo@boss.ch)
    title for contacts Fullname (address), eg. James Bond (007@bond.ch)
    """

    @property
    def only_users(self):
        return True

    def getTerm(self, value, brain=None):
        email, id_ = value.split(':', 1)

        query = self.base_query.filter(User.userid == id_)
        query = query.filter((User.email == email) | (User.email2 == email))
        user_result = query.all()
        if user_result:
            user = user_result[0]
            title = u'{} ({}, {})'.format(user.fullname(),
                                          user.userid, email)

        else:
            if not brain:
                catalog = api.portal.get_tool('portal_catalog')
                brain = catalog.unrestrictedSearchResults(
                    portal_type=CONTACT_TYPE,
                    id=id_)[0]

            if email not in [brain.email, brain.email2]:
                raise ValueError

            title = u'{} ({})'.format(brain.Title.decode('utf-8'), email)

        token = value
        return SimpleTerm(value, token, title)

    def getTermByToken(self, token):
        if not token:
            raise LookupError('Expect a userid')

        try:
            first, second = token.split(':', 1)
        except ValueError:
            raise LookupError('A token "userid:email" is required.')

        try:
            value = token
            return self.getTerm(value)
        except (ValueError, IndexError):
            raise LookupError

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.base_query,
            [User.userid, User.firstname, User.lastname, User.email],
            text_filters)

        query = query.filter_by(active=True)
        query = query.order_by(asc(func.lower(User.lastname)),
                               asc(func.lower(User.firstname)))

        for user in query:
            if user.email:
                self.terms.append(
                    self.getTerm(u'{}:{}'.format(user.email, user.userid)))
            if user.email2:
                self.terms.append(
                    self.getTerm(u'{}:{}'.format(user.email2, user.userid)))

        self._extend_terms_with_contacts(query_string)
        return self.terms

    def _extend_terms_with_contacts(self, query_string):
        catalog = api.portal.get_tool('portal_catalog')

        if not query_string.endswith('*'):
            query_string += '*'

        query = {'portal_type': CONTACT_TYPE,
                 'SearchableText': query_string}

        for brain in catalog.unrestrictedSearchResults(**query):
            if brain.email:
                self.terms.append(self.getTerm(
                    u'{}:{}'.format(brain.email, brain.id.decode('utf-8')),
                    brain))

            if brain.email2:
                self.terms.append(self.getTerm(
                    u'{}:{}'.format(brain.email2, brain.id.decode('utf-8')),
                    brain))


@implementer(IContextSourceBinder)
class AllEmailContactsAndUsersSourceBinder(object):

    def __call__(self, context):
        return AllEmailContactsAndUsersSource(context)


@implementer(IQuerySource)
class ContactsSource(UsersContactsInboxesSource):

    def getTerm(self, value, brain=None):
        if not ActorLookup(value).is_contact():
            raise ValueError('Value is not a contact token')

        catalog = api.portal.get_tool('portal_catalog')
        brain = catalog.unrestrictedSearchResults(
            portal_type=CONTACT_TYPE,
            contactid=value)[0]
        actor = Actor.contact(brain.contactid, contact=brain)
        token = value
        title = actor.get_label()
        return SimpleTerm(value, token, title)

    def getTermByToken(self, token):
        """Should raise LookupError if term could not be found.
        Check zope.schema.interfaces.IVocabularyTokenized
        """
        if not token:
            raise LookupError('Expect a userid')

        try:
            value = token
            return self.getTerm(value)
        except (IndexError, ValueError):
            raise LookupError

    def search(self, query_string):
        self.terms = []
        self._extend_terms_with_contacts(query_string)
        return self.terms


@implementer(IContextSourceBinder)
class ContactsSourceBinder(object):

    def __call__(self, context):
        return ContactsSource(context)
