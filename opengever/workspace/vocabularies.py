from opengever.workspace.interfaces import IWorkspaceFolder
from opengever.workspace.participation import PARTICIPATION_ROLES
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from Products.CMFPlone.utils import safe_unicode
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
