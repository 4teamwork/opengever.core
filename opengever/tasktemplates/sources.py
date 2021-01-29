from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.actor import INTERACTIVE_ACTORS
from opengever.ogds.base.actor import InteractiveActor
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.sources import UsersContactsInboxesSource
from z3c.formwidget.query.interfaces import IQuerySource
from zope.interface import implementer
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm


@implementer(IQuerySource)
class TaskTemplateIssuerSource(UsersContactsInboxesSource):
    """Source of all users. Thats the UsersContactsInboxesSource
    extended by the interactive users.
    """

    def getTerm(self, value=None, brain=None, solr_doc=None):
        if ActorLookup(value).is_interactive_actor():
            return SimpleTerm(value, value, InteractiveActor(value).get_label())
        else:
            return super(TaskTemplateIssuerSource, self).getTerm(value,
                                                                 brain=brain,
                                                                 solr_doc=solr_doc)

    def search(self, query_string):
        self.terms = super(TaskTemplateIssuerSource, self).search(query_string)
        self._extend_terms_with_interactive_users(query_string)
        return self.terms

    def _extend_terms_with_interactive_users(self, query_string):
        for actor_data in INTERACTIVE_ACTORS:
            actor = InteractiveActor(actor_data.get('id'))
            if query_string.lower() in actor.get_label().lower():
                self.terms.insert(0, self.getTerm(actor.identifier))


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
        if ActorLookup(value).is_interactive_actor():
            return SimpleTerm(value, value, InteractiveActor(value).get_label())
        else:
            return super(TaskResponsibleSource, self).getTerm(value)

    def search(self, query_string):
        self.terms = super(TaskResponsibleSource, self).search(query_string)
        self._extend_terms_with_interactive_users(query_string)
        return self.terms

    def _extend_terms_with_interactive_users(self, query_string):
        for actor_data in INTERACTIVE_ACTORS:
            actor = InteractiveActor(actor_data.get('id'))
            if query_string.lower() in actor.get_label().lower():
                self.terms.insert(0, self.getTerm(actor.identifier))


@implementer(IContextSourceBinder)
class TaskResponsibleSourceBinder(AllUsersInboxesAndTeamsSourceBinder):

    def __call__(self, context):
        return TaskResponsibleSource(
            context,
            only_current_orgunit=self.only_current_orgunit,
            only_current_inbox=self.only_current_inbox,
            include_teams=self.include_teams)
