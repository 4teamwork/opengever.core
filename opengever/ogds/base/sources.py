from ftw.solr.interfaces import ISolrSearch
from opengever.base.model import create_session
from opengever.base.query import extend_query_with_textfilter
from opengever.contact.contact import IContact
from opengever.contact.service import CONTACT_TYPE
from opengever.ogds.base import _
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.sharing.interfaces import ISharingConfiguration
from opengever.workspace.utils import get_workspace_user_ids
from plone import api
from sqlalchemy import func
from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.sql.expression import asc
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
import re


@implementer(IQuerySource)
class BaseQuerySoure(object):

    def __init__(self, context, **kwargs):
        self.context = context
        self.terms = []

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

    def search(self):
        raise NotImplementedError()

    def getTerm(self, value):
        raise NotImplementedError()

    def getTermByToken(self, token):
        raise NotImplementedError()


class BaseMultipleSourcesQuerySource(BaseQuerySoure):
    """Use this querysource as a baseclass if you need
    the results of different query-sources.
    """
    def __init__(self, context):
        super(BaseMultipleSourcesQuerySource, self).__init__(context)
        self.source_instances = [source_class(
            context) for source_class in self.source_classes]

    @property
    def source_classes(self):
        """Defines multiple IQuerySource-classes which should be processed.

        @return: List of classes implementing the IQuerySource interface.
        """
        raise NotImplementedError()

    def getTerm(self, value):
        term = None
        for source in self.source_instances:
            try:
                term = source.getTerm(value)
            except LookupError:
                continue

            if term:
                break

        if not term:
            raise LookupError

        return term

    def getTermByToken(self, token):
        term = None
        for source in self.source_instances:
            try:
                term = source.getTerm(token)
            except LookupError:
                continue

            if term:
                break

        if not term:
            raise LookupError

        return term

    def search(self, query_string):
        self.terms = []
        for source in self.source_instances:
            self.terms.extend(source.search(query_string))

        return self.terms


class AllUsersInboxesAndTeamsSource(BaseQuerySoure):
    """This example of a IQuerySource is taken from the
    plone.formwidget.autocomplete
    """

    def __init__(self, context, **kwargs):
        super(AllUsersInboxesAndTeamsSource, self).__init__(context, **kwargs)
        self.client_id = self.get_client_id()

        self.only_current_orgunit = kwargs.get('only_current_orgunit', False)
        self.only_active_orgunits = kwargs.get('only_active_orgunits', True)
        self.only_visible_orgunits = kwargs.get('only_visible_orgunits', True)
        self.only_current_inbox = kwargs.get('only_current_inbox', False)
        self.include_teams = kwargs.get('include_teams', False)

    @property
    def only_users(self):
        return False

    @property
    def base_query(self):
        """A base query which joins the user and orgunits together if the
        `only_users` flag is enabled.
        """
        models = (User, ) if self.only_users else (User, OrgUnit)
        return create_session().query(*models)

    @property
    def search_query(self):
        """A search query which joins the user and orgunits together and also
        filters the query based on some options:
            - only_users: Decide if only the user model will be returned
            - only_current_orgunit: Decide if only the current Orgunit will
              be queried.
            - only_active_orgunits: Filter out actors that don't have an org
              unit at all, or an inactive one (true by default).
            - only_visible_orgunits: Filter out actors that don't have an org
              unit at all, or a hidden one (true by default).
        """
        models = (User, ) if self.only_users else (User, OrgUnit)
        query = create_session().query(*models)

        # When filtering by orgunit criteria, join tables accordingly
        if self.only_active_orgunits or self.only_current_orgunit:
            query = query.join(OrgUnit.users_group) \
                         .join(Group.users)

        if self.only_active_orgunits:
            query = query.filter(OrgUnit.enabled == True)  # noqa

        if self.only_visible_orgunits:
            query = query.filter(OrgUnit.hidden == False)  # noqa

        if self.only_current_orgunit:
            query = query.filter(OrgUnit.unit_id == self.client_id)

        return query

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
        """Should raise LookupError if term could not be found.
        Check zope.schema.interfaces.IVocabularyTokenized
        """
        orgunit_id, userid = (None, None)

        if not token:
            raise LookupError('A token "unit_id:userid" is required.')
        try:
            value = token
            return self.getTerm(value)
        except orm.exc.NoResultFound:
            raise LookupError

    def search(self, query_string):
        self.terms = []
        # Ignore colons to support queries on inboxes-id.
        query_string = query_string.replace(':', ' ')

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.search_query,
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
        query = query.filter(OrgUnit.enabled == True)  # noqa
        query = query.filter(OrgUnit.hidden == False)  # noqa

        if self.only_current_inbox:
            query = query.filter(OrgUnit.unit_id == self.client_id)

        query = extend_query_with_textfilter(
            query,
            [OrgUnit.title, OrgUnit.unit_id],
            text_filters)

        for orgunit in query:
            self.terms.insert(0, self.getTerm(orgunit.inbox().id()))

    def _extend_terms_with_teams(self, text_filters):
        query = Team.query.filter(Team.active == True)  # noqa
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
                 only_active_orgunits=True,
                 only_visible_orgunits=True,
                 only_current_inbox=False,
                 include_teams=False):

        self.only_current_orgunit = only_current_orgunit
        self.only_active_orgunits = only_active_orgunits
        self.only_visible_orgunits = only_visible_orgunits
        self.only_current_inbox = only_current_inbox
        self.include_teams = include_teams

    def __call__(self, context):
        return AllUsersInboxesAndTeamsSource(
            context,
            only_current_orgunit=self.only_current_orgunit,
            only_active_orgunits=self.only_active_orgunits,
            only_visible_orgunits=self.only_visible_orgunits,
            only_current_inbox=self.only_current_inbox,
            include_teams=self.include_teams)


class UsersContactsInboxesSource(AllUsersInboxesAndTeamsSource):

    @property
    def only_users(self):
        return True

    def getTerm(self, value=None, brain=None, solr_doc=None):

        if solr_doc is not None:
            value = u'contact:{}'.format(solr_doc[u'id'])
            title = u'{} ({})'.format(solr_doc[u'Title'], solr_doc[u'email'])
            return SimpleTerm(value, title=title)

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
            self.search_query,
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
        solr = getUtility(ISolrSearch)
        resp = solr.search(query=u'SearchableText:{}* AND object_provides:{}'.format(
            query_string,
            IContact.__identifier__))
        for result in resp.docs:
            self.terms.append(self.getTerm(solr_doc=result))


@implementer(IContextSourceBinder)
class UsersContactsInboxesSourceBinder(object):

    def __init__(self,
                 only_current_orgunit=False,
                 only_active_orgunits=True,
                 only_current_inbox=False,
                 include_teams=False):

        self.only_current_orgunit = only_current_orgunit
        self.only_active_orgunits = only_active_orgunits
        self.only_current_inbox = only_current_inbox
        self.include_teams = include_teams

    def __call__(self, context):
        return UsersContactsInboxesSource(
            context,
            only_current_orgunit=self.only_current_orgunit,
            only_active_orgunits=self.only_active_orgunits,
            only_current_inbox=self.only_current_inbox,
            include_teams=self.include_teams)


class AllUsersSource(AllUsersInboxesAndTeamsSource):
    """Vocabulary of all users.
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

        value = token
        return self.getTerm(value)

    def getTerm(self, value):
        try:
            user = self.base_query.filter(User.userid == value).one()
        except orm.exc.NoResultFound:
            raise LookupError(
                'No row was found with userid: {}'.format(value))

        token = value
        title = u'{} ({})'.format(user.fullname(),
                                  user.userid)
        return SimpleTerm(value, token, title)

    def search(self, query_string):
        self.terms = []

        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.search_query,
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

    def __init__(self,
                 only_current_orgunit=False,
                 only_active_orgunits=True):

        self.only_current_orgunit = only_current_orgunit
        self.only_active_orgunits = only_active_orgunits

    def __call__(self, context):
        return AllUsersSource(
            context,
            only_current_orgunit=self.only_current_orgunit,
            only_active_orgunits=self.only_active_orgunits,
        )


class AssignedUsersSource(AllUsersSource):
    """Vocabulary of all users assigned to the current admin unit.
    """

    @property
    def search_only_active_users(self):
        return True

    @property
    def search_query(self):
        admin_unit = get_current_admin_unit()
        return create_session().query(User) \
            .filter(User.userid == groups_users.columns.userid) \
            .filter(groups_users.columns.groupid == OrgUnit.users_group_id) \
            .filter(OrgUnit.admin_unit_id == admin_unit.unit_id) \
            .filter(OrgUnit.enabled == True)  # noqa


@implementer(IContextSourceBinder)
class AssignedUsersSourceBinder(object):

    def __call__(self, context):
        return AssignedUsersSource(context)


class PotentialWorkspaceMembersSource(AssignedUsersSource):
    """Vocabulary of all users assigned to the current admin unit not yet
    members of the current workspace.
    This is also used for checking whether a user can be added to a workspace,
    the base_query therefore also needs to filter out actual members
    """

    @property
    def base_query(self):
        query = super(PotentialWorkspaceMembersSource, self).base_query
        return self._extend_query_with_workspace_filter(query)

    @property
    def search_query(self):
        query = super(PotentialWorkspaceMembersSource, self).search_query
        return self._extend_query_with_workspace_filter(query)

    def _extend_query_with_workspace_filter(self, query):
        userids = list(get_workspace_user_ids(self.context))
        # Avoid filter for an empty list.
        if userids:
            query = query.filter(User.userid.notin_(userids))
        return query


@implementer(IContextSourceBinder)
class PotentialWorkspaceMembersSourceBinder(object):

    def __call__(self, context):
        return PotentialWorkspaceMembersSource(context)


class ActualWorkspaceMembersSource(AssignedUsersSource):
    """Vocabulary of all users assigned to the current admin unit and
    members of the current workspace.
    The base query is not overwritten here, as this is used as source
    for ToDo responsibles, which should remain valid even when a user's
    permissions on a workspace are revoked (invitation deleted).
    """

    @property
    def search_query(self):
        query = super(ActualWorkspaceMembersSource, self).search_query
        return self._extend_query_with_workspace_filter(query)

    def _extend_query_with_workspace_filter(self, query):
        userids = list(get_workspace_user_ids(self.context))
        if userids:
            query = query.filter(User.userid.in_(userids))
        else:
            # Avoid filter for an empty list.
            query = query.filter(sql.false())
        return query

    def getTerm(self, value):
        """We only need the user fullname as title without the userid in
        brackets.
        """
        try:
            user = self.base_query.filter(User.userid == value).one()
        except orm.exc.NoResultFound:
            raise LookupError(
                'No row was found with userid: {}'.format(value))
        return SimpleTerm(value, value, user.fullname())


@implementer(IContextSourceBinder)
class ActualWorkspaceMembersSourceBinder(object):

    def __call__(self, context):
        return ActualWorkspaceMembersSource(context)


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

    def getTerm(self, value=None, brain=None, solr_doc=None):

        if solr_doc is not None:
            value = u'{}:{}'.format(solr_doc[u'email'], solr_doc[u'id'])
            title = u'{} ({})'.format(solr_doc[u'Title'], solr_doc[u'email'])
            return SimpleTerm(value, title=title)

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
            self.search_query,
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
        solr = getUtility(ISolrSearch)
        resp = solr.search(query=u'SearchableText:{}* AND object_provides:{}'.format(
            query_string,
            IContact.__identifier__))
        for result in resp.docs:
            if 'email' in result:
                self.terms.append(self.getTerm(solr_doc=result))
            if 'email2' in result:
                self.terms.append(self.getTerm(solr_doc={
                    'email': result['email2'],
                    'id': result['id'],
                    'Title': result['Title'],
                }))


@implementer(IContextSourceBinder)
class AllEmailContactsAndUsersSourceBinder(object):

    def __call__(self, context):
        return AllEmailContactsAndUsersSource(context)


class ContactsSource(UsersContactsInboxesSource):

    def getTerm(self, value=None, brain=None, solr_doc=None):

        if solr_doc is not None:
            value = u'contact:{}'.format(solr_doc[u'id'])
            title = u'{} ({})'.format(solr_doc[u'Title'], solr_doc[u'email'])
            return SimpleTerm(value, title=title)

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


class BaseSQLModelSource(BaseQuerySoure):

    model_class = None

    @property
    def base_query(self):
        """"""
        raise NotImplementedError()

    def getTerm(self, value):
        obj = self.model_class.get(value)
        if not obj:
            raise LookupError
        return SimpleTerm(obj.id(), obj.id(), obj.label())

    def getTermByToken(self, token):
        """ Should raise LookupError if term could not be found.
        Check zope.schema.interfaces.IVocabularyTokenized
        """
        if not token:
            raise LookupError('A token is required.')

        try:
            value = token
            return self.getTerm(value)
        except orm.exc.NoResultFound:
            raise LookupError

    def search(self, query_string):
        self.terms = []
        query = self.search_query.by_searchable_text(query_string.split(' '))

        for result in query:
            self.terms.append(self.getTerm(result.id()))

        return self.terms


class CurrentAdminUnitOrgUnitsSource(BaseSQLModelSource):

    model_class = OrgUnit

    @property
    def base_query(self):
        admin_unit = get_current_admin_unit()
        return OrgUnit.query.filter(OrgUnit.admin_unit_id == admin_unit.unit_id) \
                            .filter(OrgUnit.enabled == True)  # noqa

    @property
    def search_query(self):
        return self.base_query


@implementer(IContextSourceBinder)
class CurrentAdminUnitOrgUnitsSourceBinder(object):

    def __call__(self, context):
        return CurrentAdminUnitOrgUnitsSource(context)


class FilterMixin(object):
    """Filters the searched terms by white and black-listed groups
    """

    def search(self, query_string):
        terms = super(FilterMixin, self).search(query_string)
        black_list_prefix = api.portal.get_registry_record(
            'black_list_prefix', ISharingConfiguration)
        white_list_prefix = api.portal.get_registry_record(
            'white_list_prefix', ISharingConfiguration)

        def terms_filter(term):
            if re.search(black_list_prefix, term.value):
                if re.search(white_list_prefix, term.value):
                    return True
                return False
            return True

        terms = filter(terms_filter, terms)
        return terms


class AllGroupsSource(BaseSQLModelSource):

    model_class = Group

    @property
    def base_query(self):
        return Group.query.filter(Group.active == True)  # noqa

    @property
    def search_query(self):
        return self.base_query


class AllFilteredGroupsSourcePrefixed(FilterMixin, AllGroupsSource):
    """Prefixes the term-tokens with a string. This allows us to
    distinguish the group term from other terms if you use it in a
    multi-query-source.
    """
    GROUP_PREFIX = 'group:'

    def getTerm(self, value):
        obj = self.model_class.get(value.split(self.GROUP_PREFIX)[-1])
        if not obj:
            raise LookupError
        return SimpleTerm(obj.id(),
                          '{}{}'.format(self.GROUP_PREFIX, obj.id()),
                          obj.label())


class AllFilteredGroupsSource(FilterMixin, AllGroupsSource):
    """Filters the searched terms by white and black-listed groups
    """
    pass


@implementer(IContextSourceBinder)
class AllFilteredGroupsSourceBinder(object):

    def __call__(self, context):
        return AllFilteredGroupsSource(context)


@implementer(IContextSourceBinder)
class AllGroupsSourceBinder(object):

    def __call__(self, context):
        return AllGroupsSource(context)


class AllUsersAndGroupsSource(BaseMultipleSourcesQuerySource):

    source_classes = [AllFilteredGroupsSourcePrefixed, AllUsersSource]


@implementer(IContextSourceBinder)
class AllUsersAndGroupsSourceBinder(object):

    def __call__(self, context):
        return AllUsersAndGroupsSource(context)
