from opengever.ogds.base.sources import UsersContactsInboxesSource
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.tasktemplates import _
from z3c.formwidget.query.interfaces import IQuerySource
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm


def interactive_users():
    return {
        'responsible': translate(_(u'interactive_user_responsible',
                                   default=u'Responsible'),
                                 context=getRequest()),

        'current_user': translate(_(u'interactive_user_current_user',
                                    default=u'Current user'),
                                  context=getRequest())
    }


@implementer(IQuerySource)
class TaskTemplateIssuerSource(UsersContactsInboxesSource):
    """Source of all users. Thats the UsersContactsInboxesSource
    extended by the interactive users.
    """

    def getTerm(self, value, brain=None):
        users = interactive_users()
        if value in users:
            token = value
            return SimpleTerm(value, token, users[value])

        else:
            return super(TaskTemplateIssuerSource, self).getTerm(value,
                                                                 brain=brain)

    def search(self, query_string):
        self.terms = super(TaskTemplateIssuerSource, self).search(query_string)
        self._extend_terms_with_interactive_users(query_string)
        return self.terms

    def _extend_terms_with_interactive_users(self, query_string):
        for value, title in interactive_users().items():
            if query_string.lower() in title.lower():
                self.terms.insert(0, self.getTerm(value))


@implementer(IContextSourceBinder)
class TaskTemplateIssuerSourceBinder(object):

    def __call__(self, context):
        return TaskTemplateIssuerSource(context)


@implementer(IQuerySource)
class TaskResponsibleSource(AllUsersInboxesAndTeamsSource):
    """Source with the default users and clients extended with the
    interactive users.
    """

    def getTerm(self, value):
        special_users = interactive_users()
        if value.startswith('interactive_users:'):
            special_user = value.split(':', 1)[1]
        elif value in special_users:
            special_user = value
        else:
            special_user = None

        if special_user:
            token = 'interactive_users:' + special_user
            value = token
            return SimpleTerm(value, token, special_users[special_user])

        else:
            return super(TaskResponsibleSource, self).getTerm(value)

    def search(self, query_string):
        self.terms = super(TaskResponsibleSource, self).search(query_string)
        self._extend_terms_with_interactive_users(query_string)
        return self.terms

    def _extend_terms_with_interactive_users(self, query_string):
        for value, title in interactive_users().items():
            if query_string.lower() in title.lower():
                self.terms.insert(0, self.getTerm(value))


@implementer(IContextSourceBinder)
class TaskResponsibleSourceBinder(object):

    def __call__(self, context):
        return TaskResponsibleSource(context)
