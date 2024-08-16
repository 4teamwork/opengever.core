from opengever.base.visible_users_and_groups_filter import visible_users_and_groups_filter
from opengever.ogds.base.sources import AllUsersSource
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSource
from opengever.ogds.models.user import User
from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import func
from sqlalchemy.sql.expression import asc
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class RolesVocabulary(object):

    def __call__(self, context):
        terms = []
        for role in PARTICIPATION_ROLES.values():
            if not role.managed:
                continue
            terms.append(SimpleTerm(value=role.id,
                                    token=role.id,
                                    title=safe_unicode(
                                        role.translated_title(getRequest()))))

        return SimpleVocabulary(terms)


@implementer(IVocabularyFactory)
class PossibleWorkspaceFolderParticipantsVocabulary(object):
    """This vocabulary is used in a workspace folder to get the available
    participations based on the participations in the parent folder or
    workspace.

    A workspace folder can block role inheritance. Only participants from the
    parent folder are allowed to add as new participant in a folder.
    """
    def __call__(self, context):
        if not IWorkspaceFolder.providedBy(context):
            return SimpleVocabulary([])

        terms = []

        parent_manager = ManageParticipants(context.get_parent_with_local_roles(), context.REQUEST)
        context_manager = ManageParticipants(context.get_context_with_local_roles(), context.REQUEST)

        context_participants = [participant.get('token') for participant
                                in context_manager.get_participants()]
        for participant in parent_manager.get_participants():
            if participant.get('token') in context_participants:
                # Participant already participated.
                continue

            terms.append(SimpleTerm(value=participant.get('token'),
                                    token=participant.get('token'),
                                    title=safe_unicode(
                                        participant.get('name'))))

        return SimpleVocabulary(terms)


class WorkspaceUserVocabulary(SimpleVocabulary):
    """provide additional functionality for retrieving terms related to workspace users.
    If a term is not found in the current vocabulary, it attempts to retrieve the term from
    AllUsersSource
    """
    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        try:
            return super(WorkspaceUserVocabulary, self).getTerm(value)
        except LookupError:
            if not visible_users_and_groups_filter.can_access_principal(value):
                return SimpleTerm('<not-found>', '<not-found>', '<not-found>')
            return AllUsersSource(api.portal.get()).getTermByToken(value)


@implementer(IVocabularyFactory)
class WorkspaceContentMembersVocabulary(object):
    """ Vocabulary of all users assigned to the current workspace.
    """
    def __call__(self, context):
        terms = []
        query = WorkspaceContentMemberUsersSource(context).search_query
        query = query.filter(User.active == True)  # noqa
        query = query.order_by(asc(func.lower(User.lastname)),
                               asc(func.lower(User.firstname)))

        for member in query.all():
            terms.append(SimpleTerm(value=member.userid,
                                    token=member.userid,
                                    title=member.fullname()))

        return WorkspaceUserVocabulary(terms)
