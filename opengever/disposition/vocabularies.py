from opengever.disposition.disposition import Disposition
from opengever.ogds.base.actor import ActorLookup
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class ArchivistVocabulary(object):

    def __call__(self, context):
        terms = []
        archivists = Disposition.get_all_archivists()
        for principal in archivists:
            term = SimpleTerm(
                value=principal,
                token=principal,
                title=ActorLookup(principal).lookup().get_label()
            )
            terms.append(term)
        return SimpleVocabulary(terms)
