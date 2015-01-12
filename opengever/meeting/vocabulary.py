from five import grok
from opengever.meeting.service import meeting_service
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class CommitteeVocabulary(grok.GlobalUtility):
    grok.provides(IVocabularyFactory)
    grok.name('opengever.meeting.CommitteeVocabulary')

    def __call__(self, context):
        terms = []

        for committee in meeting_service().all_committees():
            terms.append(SimpleTerm(value=committee,
                                    token=committee.committee_id,
                                    title=committee.title))
        return SimpleVocabulary(terms)
