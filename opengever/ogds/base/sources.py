from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.query import extend_query_with_textfilter
from opengever.ogds.models.user import User
from sqlalchemy import orm
from z3c.formwidget.query.interfaces import IQuerySource
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class AllUsersAndInboxesSource(object):
    """This example of a IQuerySource is taken from the
    plone.formwidget.autocomplete
    """

    def __init__(self, context):
        self.context = context
        self.terms = []
        self.client_id = self.get_client_id()

    @property
    def base_query(self):
        return create_session().query(User, OrgUnit) \
                               .join(OrgUnit.users_group) \
                               .join(Group.users)

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

        user, orgunit = self.base_query.filter(OrgUnit.unit_id == orgunit_id) \
                                       .filter(User.userid == userid).one()

        token = u'{}:{}'.format(orgunit_id, userid)
        title = u'{}: {} ({})'.format(orgunit.title,
                                      user.fullname(),
                                      user.email)
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
            self.base_query.filter(OrgUnit.unit_id == orgunit_id) \
                           .filter(User.userid == userid).one()
        except orm.exc.NoResultFound:
            raise LookupError

        value = token
        return self.getTerm(value)

    def search(self, query_string):
        text_filters = query_string.split(' ')
        query = extend_query_with_textfilter(
            self.base_query,
            [OrgUnit.title, OrgUnit.unit_id,
             User.userid, User.firstname, User.lastname, User.email],
            text_filters)

        query = query.filter_by(active=True)

        for user, orgunit in query.all():
            self.terms.append(
                self.getTerm(u'{}:{}'.format(orgunit.id(), user.userid)))
        return self.terms

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
class AllUsersAndInboxesSourceBinder(object):

    def __call__(self, context):
        return AllUsersAndInboxesSource(context)
