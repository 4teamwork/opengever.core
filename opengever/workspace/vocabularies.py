from opengever.workspace.participation import PARTICIPATION_ROLES
from Products.CMFPlone.utils import safe_unicode
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
                                        role.translated_title(context.REQUEST))))

        return SimpleVocabulary(terms)
